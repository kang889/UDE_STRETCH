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

const SIDE_BODY_HOLD_SECONDS = 8;
const REQUIRED_REPS = 10;
const NECK_CALF_RAISES_PER_SIDE = 8;
let neckCalfRaiseCount = {
    left: 0,
    right: 0
};

let neckCalfRaiseBaselineY = {
    left: null,
    right: null
};

let neckCalfRaiseState = {
    left: "down",
    right: "down"
};

let squatCount = 0;
let squatBaselineHipY = null;
let squatBaselineGap = null;
let squatState = "up";

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
        try {
            startButton.disabled = true;
            statusText.textContent = "Loading camera check...";

            await setupPoseLandmarker();
            await startWebcam();

            webcamRunning = true;
            statusText.textContent = "Camera started. Perform the exercise.";
            predictWebcam();
        } catch (error) {
            console.error(error);

            startButton.disabled = false;
            statusText.textContent =
                "Camera failed to start. Check browser console.";
        }
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

        const result = poseLandmarker.detectForVideo(
            video,
            performance.now()
        );

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
            message: "No body detected. Move back so your body is visible."
        };
    }

    const landmarks = result.landmarks[0];

    if (selectedStretchId === "side-body-stretch") {
        return checkSideBodyStretch(landmarks);
    }

    if (selectedStretchId === "neck-stretch-calf-raises") {
        return checkNeckStretchCalfRaises(landmarks);
    }

    if (selectedStretchId === "squat") {
        return checkSquat(landmarks);
    }

    return {
        isCorrect: false,
        side: null,
        message: "Unknown exercise."
    };
}

function checkSideBodyStretch(landmarks) {
    /*
    Check left/right upper body side lean.
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

    const leanOffset = shoulderCenterX - hipCenterX;
    const leanRatio = Math.abs(leanOffset) / shoulderWidth;

    if (leanRatio > 0.08) {
        if (leanOffset < 0) {
            return {
                isCorrect: true,
                side: "left",
                message: "Good. Hold the left side body stretch."
            };
        }

        return {
            isCorrect: true,
            side: "right",
            message: "Good. Hold the right side body stretch."
        };
    }

    return {
        isCorrect: false,
        side: null,
        message: "Lean your upper body more clearly to one side."
    };
}

function checkNeckStretchCalfRaises(landmarks) {
    /*
    Check neck side tilt while counting calf raises.
    User must complete 8 calf raises on each side.
    */
    const nose = landmarks[0];
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const leftHip = landmarks[23];
    const rightHip = landmarks[24];

    if (!areVisible([nose, leftShoulder, rightShoulder, leftHip, rightHip])) {
        return {
            isCorrect: false,
            side: null,
            message: "Make sure your face, shoulders, and body are visible."
        };
    }

    const shoulderWidth = Math.abs(leftShoulder.x - rightShoulder.x);
    const shoulderCenterX = (leftShoulder.x + rightShoulder.x) / 2;
    const headOffset = nose.x - shoulderCenterX;
    const tiltRatio = Math.abs(headOffset) / shoulderWidth;

    if (tiltRatio <= 0.1) {
        return {
            isCorrect: false,
            side: null,
            message: "Tilt your head sideways for the neck stretch."
        };
    }

    const side = headOffset < 0 ? "left" : "right";

    const bodyY =
        (leftShoulder.y + rightShoulder.y + leftHip.y + rightHip.y) / 4;

    if (neckCalfRaiseBaselineY[side] === null) {
        neckCalfRaiseBaselineY[side] = bodyY;
    }

    const upThreshold = 0.012;
    const returnThreshold = 0.005;

    if (
        neckCalfRaiseState[side] === "down" &&
        bodyY < neckCalfRaiseBaselineY[side] - upThreshold
    ) {
        neckCalfRaiseState[side] = "up";
    }

    if (
        neckCalfRaiseState[side] === "up" &&
        bodyY > neckCalfRaiseBaselineY[side] - returnThreshold
    ) {
        neckCalfRaiseCount[side] += 1;
        neckCalfRaiseState[side] = "down";
        neckCalfRaiseBaselineY[side] = bodyY;
    }

    if (neckCalfRaiseCount[side] >= NECK_CALF_RAISES_PER_SIDE) {
        completedSide[side] = true;
    }

    if (completedSide.left && completedSide.right) {
        return {
            isCorrect: true,
            side: side,
            isCountExercise: true,
            message: "Both neck stretch sides completed."
        };
    }

    return {
        isCorrect: true,
        side: side,
        isCountExercise: true,
        message:
            `${side} side calf raises: ${neckCalfRaiseCount[side]}/${NECK_CALF_RAISES_PER_SIDE}`
    };
}

function checkSquat(landmarks) {
    /*
    Count squat reps using a more forgiving hip-to-knee check.
    This works better when full-body movement is hard to capture.
    */
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const leftHip = landmarks[23];
    const rightHip = landmarks[24];
    const leftKnee = landmarks[25];
    const rightKnee = landmarks[26];

    if (!areVisible([
        leftShoulder,
        rightShoulder,
        leftHip,
        rightHip,
        leftKnee,
        rightKnee
    ])) {
        return {
            isCorrect: false,
            side: null,
            message: "Move back so your shoulders, hips, and knees are visible."
        };
    }

    const hipY = (leftHip.y + rightHip.y) / 2;
    const kneeY = (leftKnee.y + rightKnee.y) / 2;

    const shoulderY = (leftShoulder.y + rightShoulder.y) / 2;
    const torsoLength = Math.abs(hipY - shoulderY);

    const hipKneeGap = kneeY - hipY;

    if (squatBaselineHipY === null) {
        squatBaselineHipY = hipY;
        squatBaselineGap = hipKneeGap;
    }

    const hipDrop = hipY - squatBaselineHipY;

    const enoughHipDrop = hipDrop > torsoLength * 0.22;
    const closeToKnees = hipKneeGap < squatBaselineGap * 0.55;

    const isSquatDown = enoughHipDrop || closeToKnees;

    const returnedUp =
        hipY < squatBaselineHipY + torsoLength * 0.10;

    if (squatState === "up" && isSquatDown) {
        squatState = "down";

        return {
            isCorrect: true,
            side: "single",
            isCountExercise: true,
            message: `Squat detected. Stand back up. Reps: ${squatCount}/${REQUIRED_REPS}`
        };
    }

    if (squatState === "down" && returnedUp) {
        squatCount += 1;
        squatState = "up";

        squatBaselineHipY = hipY;
        squatBaselineGap = hipKneeGap;

        if (squatCount >= REQUIRED_REPS) {
            completedSide.single = true;

            return {
                isCorrect: true,
                side: "single",
                isCountExercise: true,
                message: "10 squats completed."
            };
        }

        return {
            isCorrect: true,
            side: "single",
            isCountExercise: true,
            message: `Good rep. Squats: ${squatCount}/${REQUIRED_REPS}`
        };
    }

    return {
        isCorrect: true,
        side: "single",
        isCountExercise: true,
        message: `Squats: ${squatCount}/${REQUIRED_REPS}. Lower your hips, then stand tall.`
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
    Update timer-based or count-based progress.
    */
    statusText.textContent = checkResult.message;

    if (!checkResult.isCorrect || checkResult.side === null) {
        resetActiveHoldTimers();
        return;
    }

    if (checkResult.isCountExercise) {
        updateProgressBars();
        updateCompleteButton();
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

    if (heldSeconds >= SIDE_BODY_HOLD_SECONDS) {
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
    Return progress percent for timer-based or rep-based exercises.
    */
    if (selectedStretchId === "neck-stretch-calf-raises") {
        return Math.min(
            (neckCalfRaiseCount[side] / NECK_CALF_RAISES_PER_SIDE) * 100,
            100
        );
    }

    if (selectedStretchId === "squat" && side === "single") {
        return Math.min((squatCount / REQUIRED_REPS) * 100, 100);
    }

    if (completedSide[side]) {
        return 100;
    }

    if (holdStartTime[side] === null) {
        return 0;
    }

    const heldSeconds = (performance.now() - holdStartTime[side]) / 1000;

    return Math.min(
        (heldSeconds / SIDE_BODY_HOLD_SECONDS) * 100,
        100
    );
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
        selectedStretchId === "side-body-stretch" ||
        selectedStretchId === "neck-stretch-calf-raises";

    const isComplete = needsTwoSides
        ? completedSide.left && completedSide.right
        : completedSide.single;

    if (!isComplete) {
        return;
    }

    completeButton.classList.remove("disabled-link");
    completeButton.textContent = "Exercise Verified - Complete";
    statusText.textContent = "Exercise verified. You can complete it now.";
}