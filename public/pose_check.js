/*
Uses MediaPipe Pose Landmarker to verify stretch movement.
No pose dots are shown to users.
*/

import {
    FilesetResolver,
    PoseLandmarker
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest";

const video = document.getElementById("webcam");

const startButton = document.getElementById("start-camera-button");
const completeButton = document.getElementById("complete-button");
const statusText = document.getElementById("pose-status");

const leftProgress = document.getElementById("left-progress");
const rightProgress = document.getElementById("right-progress");
const singleProgress = document.getElementById("single-progress");

const leftProgressText = document.getElementById("left-progress-text");
const rightProgressText = document.getElementById("right-progress-text");
const singleProgressText = document.getElementById("single-progress-text");

const REQUIRED_HOLD_SECONDS = 3;

let poseLandmarker = null;
let webcamRunning = false;
let lastVideoTime = -1;
let selectedStretchId = "";

let holdStartTime = {
    left: null,
    right: null,
    single: null
};

let completedSide = {
    left: false,
    right: false,
    single: false
};

if (startButton) {
    selectedStretchId = startButton.dataset.stretchId;

    startButton.addEventListener("click", async function () {
        startButton.disabled = true;
        statusText.textContent = "Loading camera check...";

        await setupPoseLandmarker();
        await startWebcam();

        webcamRunning = true;
        statusText.textContent = "Camera started. Perform the stretch.";
        predictWebcam();
    });
}

async function setupPoseLandmarker() {
    /*
    Load MediaPipe Pose Landmarker.
    */
    const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
    );

    poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
        baseOptions: {
            modelAssetPath:
                "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
            delegate: "GPU"
        },
        runningMode: "VIDEO",
        numPoses: 1,
        minPoseDetectionConfidence: 0.5,
        minPosePresenceConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
}

async function startWebcam() {
    /*
    Start browser webcam.
    */
    const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
    });

    video.srcObject = stream;

    await new Promise(function (resolve) {
        video.onloadedmetadata = resolve;
    });

    video.play();
}

function predictWebcam() {
    /*
    Run pose detection every frame.
    */
    if (!webcamRunning || !poseLandmarker) {
        return;
    }

    if (video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;

        const result = poseLandmarker.detectForVideo(video, performance.now());
        const checkResult = checkSelectedStretch(result);

        updateCompletionProgress(checkResult);
    }

    requestAnimationFrame(predictWebcam);
}

function checkSelectedStretch(result) {
    /*
    Select checking rule based on stretch id.
    */
    if (!result.landmarks || result.landmarks.length === 0) {
        return {
            isCorrect: false,
            side: null,
            message: "No body detected. Move back so your upper body is visible."
        };
    }

    const landmarks = result.landmarks[0];

    if (selectedStretchId === "neck-side-stretch") {
        return checkNeckSideStretch(landmarks);
    }

    if (selectedStretchId === "shoulder-rolls") {
        return checkShoulderRolls(landmarks);
    }

    if (selectedStretchId === "seated-torso-twist") {
        return checkSeatedTorsoTwist(landmarks);
    }

    return {
        isCorrect: false,
        side: null,
        message: "Unknown stretch."
    };
}

function checkNeckSideStretch(landmarks) {
    /*
    Check left/right neck side stretch.
    */
    const nose = landmarks[0];
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];

    if (!areVisible([nose, leftShoulder, rightShoulder])) {
        return {
            isCorrect: false,
            side: null,
            message: "Make sure your face and shoulders are visible."
        };
    }

    const shoulderWidth = Math.abs(leftShoulder.x - rightShoulder.x);
    const shoulderCenterX = (leftShoulder.x + rightShoulder.x) / 2;
    const headOffset = nose.x - shoulderCenterX;
    const tiltRatio = Math.abs(headOffset) / shoulderWidth;

    if (tiltRatio > 0.12) {
        if (headOffset < 0) {
            return {
                isCorrect: true,
                side: "left",
                message: "Good. Hold the left side neck stretch."
            };
        }

        return {
            isCorrect: true,
            side: "right",
            message: "Good. Hold the right side neck stretch."
        };
    }

    return {
        isCorrect: false,
        side: null,
        message: "Tilt your head sideways more clearly."
    };
}

let shoulderHistory = [];

function checkShoulderRolls(landmarks) {
    /*
    Check shoulder movement.
    */
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];

    if (!areVisible([leftShoulder, rightShoulder])) {
        return {
            isCorrect: false,
            side: null,
            message: "Make sure both shoulders are visible."
        };
    }

    const averageShoulderY = (leftShoulder.y + rightShoulder.y) / 2;

    shoulderHistory.push(averageShoulderY);

    if (shoulderHistory.length > 45) {
        shoulderHistory.shift();
    }

    const highest = Math.max(...shoulderHistory);
    const lowest = Math.min(...shoulderHistory);
    const movementRange = highest - lowest;

    if (movementRange > 0.025) {
        return {
            isCorrect: true,
            side: "single",
            message: "Good. Shoulder movement detected."
        };
    }

    return {
        isCorrect: false,
        side: null,
        message: "Roll your shoulders slowly in a larger motion."
    };
}

function checkSeatedTorsoTwist(landmarks) {
    /*
    Check left/right torso twist.
    */
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const leftHip = landmarks[23];
    const rightHip = landmarks[24];

    if (!areVisible([leftShoulder, rightShoulder, leftHip, rightHip])) {
        return {
            isCorrect: false,
            side: null,
            message: "Make sure your shoulders and hips are visible."
        };
    }

    const shoulderWidth = Math.abs(leftShoulder.x - rightShoulder.x);
    const shoulderCenterX = (leftShoulder.x + rightShoulder.x) / 2;
    const hipCenterX = (leftHip.x + rightHip.x) / 2;

    const twistOffset = shoulderCenterX - hipCenterX;
    const twistRatio = Math.abs(twistOffset) / shoulderWidth;

    if (twistRatio > 0.08) {
        if (twistOffset < 0) {
            return {
                isCorrect: true,
                side: "left",
                message: "Good. Hold the left torso twist."
            };
        }

        return {
            isCorrect: true,
            side: "right",
            message: "Good. Hold the right torso twist."
        };
    }

    return {
        isCorrect: false,
        side: null,
        message: "Turn your upper body slightly more to one side."
    };
}

function areVisible(points) {
    /*
    Check if landmarks are usable.
    */
    for (const point of points) {
        if (!point) {
            return false;
        }

        if (point.visibility !== undefined && point.visibility < 0.5) {
            return false;
        }
    }

    return true;
}

function updateCompletionProgress(checkResult) {
    /*
    Update one-side or two-side progress.
    */
    statusText.textContent = checkResult.message;

    if (!checkResult.isCorrect || checkResult.side === null) {
        resetActiveHoldTimers();
        return;
    }

    updateSideHold(checkResult.side);
    updateProgressBars();
    updateCompleteButton();
}

function updateSideHold(side) {
    /*
    Track how long one side is held.
    */
    const now = performance.now();

    if (completedSide[side]) {
        return;
    }

    if (holdStartTime[side] === null) {
        holdStartTime[side] = now;
    }

    const heldSeconds = (now - holdStartTime[side]) / 1000;

    if (heldSeconds >= REQUIRED_HOLD_SECONDS) {
        completedSide[side] = true;
        holdStartTime[side] = null;
    }
}

function resetActiveHoldTimers() {
    /*
    Reset active holds when pose is incorrect.
    */
    if (!completedSide.left) {
        holdStartTime.left = null;
    }

    if (!completedSide.right) {
        holdStartTime.right = null;
    }

    if (!completedSide.single) {
        holdStartTime.single = null;
    }
}

function getSidePercent(side) {
    /*
    Return progress percent for one side.
    */
    if (completedSide[side]) {
        return 100;
    }

    if (holdStartTime[side] === null) {
        return 0;
    }

    const heldSeconds = (performance.now() - holdStartTime[side]) / 1000;
    return Math.min((heldSeconds / REQUIRED_HOLD_SECONDS) * 100, 100);
}

function updateProgressBars() {
    /*
    Refresh progress bar UI.
    */
    updateOneBar(leftProgress, leftProgressText, getSidePercent("left"));
    updateOneBar(rightProgress, rightProgressText, getSidePercent("right"));
    updateOneBar(singleProgress, singleProgressText, getSidePercent("single"));
}

function updateOneBar(barElement, textElement, percent) {
    /*
    Update one progress bar.
    */
    if (!barElement || !textElement) {
        return;
    }

    const roundedPercent = Math.round(percent);

    barElement.style.width = `${roundedPercent}%`;
    textElement.textContent = `${roundedPercent}%`;
}

function updateCompleteButton() {
    /*
    Unlock complete button when required checks are done.
    */
    const needsTwoSides =
        selectedStretchId === "neck-side-stretch" ||
        selectedStretchId === "seated-torso-twist";

    const isComplete = needsTwoSides
        ? completedSide.left && completedSide.right
        : completedSide.single;

    if (!isComplete) {
        return;
    }

    completeButton.classList.remove("disabled-link");
    completeButton.textContent = "Stretch Verified - Complete";
    statusText.textContent = "Stretch verified. You can complete it now.";
}