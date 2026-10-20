import { EditorView, basicSetup } from "https://esm.sh/codemirror";
import { EditorState, Compartment } from "https://esm.sh/@codemirror/state";
import {
    defaultHighlightStyle,
    syntaxHighlighting
} from "https://esm.sh/@codemirror/language";
import { python } from "https://esm.sh/@codemirror/lang-python";
import { javascript } from "https://esm.sh/@codemirror/lang-javascript";
import { cpp } from "https://esm.sh/@codemirror/lang-cpp";
import { java } from "https://esm.sh/@codemirror/lang-java";

const API_BASE_URL = "https://judgey-compiler-4.onrender.com/";

const runButton = document.getElementById("runButton");
const languageSelector = document.getElementById("language");
const outputText = document.getElementById("outputText");
const errorCount = document.getElementById("errorCount");
const volumeButton = document.getElementById("volumeButton");
const backgroundLayer = document.getElementById("backgroundLayer");

let errors = 0;
let currentBackgroundLevel = -1;
let currentMusic = null;
let currentMusicLevel = -1;
let isMuted = false;
let autoplayBlocked = false;
let backgroundChanging = false;

const backgroundPictures = [
    "/pictures/picture-1.png",
    "/pictures/picture-2.png",
    "/pictures/picture-3.png",
    "/pictures/picture-4.png",
    "/pictures/picture-5.png"
];

const musicTracks = [
    "/sounds/music-1.mp3",
    "/sounds/music-2.mp3",
    "/sounds/music-3.mp3",
    "/sounds/music-4.mp3",
    "/sounds/music-5.mp3"
];

backgroundPictures.forEach((picture) => {
    const image = new Image();
    image.src = picture;
});

function changeBackground(level) {
    level = Math.max(0, Math.min(level, 4));

    if (
        currentBackgroundLevel === level ||
        backgroundChanging
    ) {
        return;
    }

    currentBackgroundLevel = level;
    backgroundChanging = true;

    const newImage = new Image();

    newImage.onload = () => {
        backgroundLayer.style.opacity = "0";

        setTimeout(() => {
            backgroundLayer.style.backgroundImage =
                `url("${backgroundPictures[level]}")`;

            backgroundLayer.style.opacity = "1";

            setTimeout(() => {
                backgroundChanging = false;
            }, 700);
        }, 350);
    };

    newImage.src = backgroundPictures[level];
}

function updateVolumeIcons() {
    const volumeOnIcon =
        document.getElementById("volumeOnIcon");

    const volumeOffIcon =
        document.getElementById("volumeOffIcon");

    if (isMuted) {
        volumeOnIcon.style.display = "none";
        volumeOffIcon.style.display = "block";
    } else {
        volumeOnIcon.style.display = "block";
        volumeOffIcon.style.display = "none";
    }
}

function startMusic() {
    if (isMuted) {
        return;
    }

    if (!currentMusic) {
        currentMusic = new Audio(musicTracks[errors]);
        currentMusic.loop = true;
        currentMusic.volume = 0.5;
        currentMusic.muted = false;
    }

    currentMusic.play()
        .then(() => {
            autoplayBlocked = false;
        })
        .catch(() => {
            autoplayBlocked = true;
        });
}

function changeMusic(level) {
    level = Math.max(0, Math.min(level, 4));

    if (
        currentMusicLevel === level &&
        currentMusic
    ) {
        startMusic();
        return;
    }

    currentMusicLevel = level;

    if (currentMusic) {
        currentMusic.pause();
        currentMusic.currentTime = 0;
    }

    currentMusic = new Audio(musicTracks[level]);
    currentMusic.loop = true;
    currentMusic.volume = 0.5;
    currentMusic.muted = isMuted;

    currentMusic.play()
        .then(() => {
            autoplayBlocked = false;
        })
        .catch(() => {
            autoplayBlocked = true;
        });
}

function updateHorrorLevel() {
    errorCount.textContent = errors;

    changeBackground(errors);
    changeMusic(errors);
}

function tryStartMusic() {
    if (!isMuted && autoplayBlocked) {
        startMusic();
    }
}

document.addEventListener("click", tryStartMusic, {
    once: true
});

document.addEventListener("keydown", tryStartMusic, {
    once: true
});

document.addEventListener("pointerdown", tryStartMusic, {
    once: true
});

volumeButton.addEventListener("click", () => {
    if (!currentMusic) {
        startMusic();
        return;
    }

    if (autoplayBlocked && !isMuted) {
        startMusic();
        return;
    }

    isMuted = !isMuted;

    currentMusic.muted = isMuted;

    updateVolumeIcons();

    if (!isMuted) {
        startMusic();
    }
});

const editorTheme = EditorView.theme({
    "&": {
        color: "#f8f8f2",
        backgroundColor: "#111318"
    },

    ".cm-content": {
        caretColor: "#ffffff"
    },

    ".cm-cursor": {
        borderLeftColor: "#ffffff"
    },

    ".cm-gutters": {
        backgroundColor: "#111318",
        color: "#777777",
        borderRight: "1px solid #333333"
    },

    ".cm-activeLine": {
        backgroundColor: "#191c22"
    },

    ".cm-activeLineGutter": {
        backgroundColor: "#191c22"
    },

    ".cm-selectionBackground": {
        backgroundColor: "#333b4a"
    },

    "&.cm-focused .cm-selectionBackground": {
        backgroundColor: "#333b4a"
    }
});

const languageCompartment =
    new Compartment();

const exampleCode = {
    python:
`print("Hello, Judgey Compiler!")`,

    javascript:
`console.log("Hello, Judgey Compiler!");`,

    c:
`#include <stdio.h>

int main() {
    printf("Hello, Judgey Compiler!");
    return 0;
}`,

    cpp:
`#include <iostream>

int main() {
    std::cout << "Hello, Judgey Compiler!";
    return 0;
}`,

    java:
`public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, Judgey Compiler!");
    }
}`
};

const editor = new EditorView({
    state: EditorState.create({
        doc: exampleCode.python,

        extensions: [
            basicSetup,

            languageCompartment.of(
                python()
            ),

            syntaxHighlighting(
                defaultHighlightStyle
            ),

            editorTheme
        ]
    }),

    parent:
        document.getElementById("editor")
});

languageSelector.addEventListener("change", () => {
    const selectedLanguage =
        languageSelector.value;

    let languageExtension;

    if (selectedLanguage === "python") {
        languageExtension = python();
    }

    else if (selectedLanguage === "javascript") {
        languageExtension = javascript();
    }

    else if (selectedLanguage === "c") {
        languageExtension = cpp();
    }

    else if (selectedLanguage === "cpp") {
        languageExtension = cpp();
    }

    else if (selectedLanguage === "java") {
        languageExtension = java();
    }

    editor.dispatch({
        effects:
            languageCompartment.reconfigure(
                languageExtension
            )
    });

    editor.dispatch({
        changes: {
            from: 0,
            to: editor.state.doc.length,
            insert: exampleCode[selectedLanguage]
        }
    });
});

runButton.addEventListener("click", async () => {
    const code =
        editor.state.doc.toString();

    const selectedLanguage =
        languageSelector.value;

    outputText.textContent =
        "Compiling...";

    runButton.disabled = true;
    runButton.textContent =
        "RUNNING...";

    try {
        const response =
            await fetch(`${API_BASE_URL}/compile`, {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        language:
                            selectedLanguage,

                        code:
                            code
                    })
            });

        const result =
            await response.json();

        if (result.success) {
    outputText.textContent =
        result.output ||
        "Program finished successfully.";

    errors = 0;
}

else {
    outputText.textContent =
        result.error ||
        "Unknown compilation error.";

    errors =
        Number(result.errors) || 1;
}

        updateHorrorLevel();

    } catch (error) {
        errors = 1;

        outputText.textContent =
            "Could not connect to the compiler.\n\n" +
            error.message;

        updateHorrorLevel();
    }

    runButton.disabled = false;
    runButton.textContent =
        "RUN CODE";
});

errorCount.textContent = "0";

updateVolumeIcons();
changeBackground(0);
changeMusic(0);