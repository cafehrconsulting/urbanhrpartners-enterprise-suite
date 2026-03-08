(function () {
    "use strict";

    class XiomyVoice {
        constructor() {
            this.synth = window.speechSynthesis || null;
            this.voice = null;
            this.availableVoices = [];
            this.isSupported = !!this.synth;
            this.isInitialized = false;
            this.defaultRate = 1.0;
            this.defaultPitch = 1.0;
            this.defaultVolume = 1.0;
            this.preferredVoiceNames = [
                "Google US English",
                "Google UK English Female",
                "Microsoft Aria Online (Natural) - English (United States)",
                "Microsoft Jenny Online (Natural) - English (United States)",
                "Microsoft Zira Desktop - English (United States)",
                "Samantha",
                "Karen",
                "Moira",
                "Ava",
                "Female"
            ];

            this.initialize();
        }

        initialize() {
            if (!this.isSupported) {
                console.warn("Speech synthesis is not supported in this browser.");
                return;
            }

            this.loadVoices();

            if (typeof this.synth.onvoiceschanged !== "undefined") {
                this.synth.onvoiceschanged = () => {
                    this.loadVoices();
                };
            }

            this.isInitialized = true;
        }

        loadVoices() {
            if (!this.synth) {
                return;
            }

            const voices = this.synth.getVoices();
            if (!voices || !voices.length) {
                return;
            }

            this.availableVoices = voices.slice();
            this.voice = this.selectBestVoice(this.availableVoices);
        }

        selectBestVoice(voices) {
            if (!voices || !voices.length) {
                return null;
            }

            const lowerPriorityNames = this.preferredVoiceNames.map(function (name) {
                return String(name).toLowerCase();
            });

            for (let i = 0; i < voices.length; i += 1) {
                const voiceName = String(voices[i].name || "").toLowerCase();
                if (lowerPriorityNames.some(function (preferred) { return voiceName.includes(preferred); })) {
                    return voices[i];
                }
            }

            for (let i = 0; i < voices.length; i += 1) {
                const voiceName = String(voices[i].name || "").toLowerCase();
                if (voiceName.includes("female")) {
                    return voices[i];
                }
            }

            for (let i = 0; i < voices.length; i += 1) {
                const lang = String(voices[i].lang || "").toLowerCase();
                if (lang.startsWith("en-us")) {
                    return voices[i];
                }
            }

            for (let i = 0; i < voices.length; i += 1) {
                const lang = String(voices[i].lang || "").toLowerCase();
                if (lang.startsWith("en")) {
                    return voices[i];
                }
            }

            return voices[0];
        }

        speak(message, options) {
            if (!this.isSupported || !this.synth) {
                console.warn("Speech synthesis unavailable. Message:", message);
                return false;
            }

            if (!message || typeof message !== "string") {
                return false;
            }

            const settings = options || {};
            const utterance = new SpeechSynthesisUtterance(message);

            if (!this.voice && this.availableVoices.length) {
                this.voice = this.selectBestVoice(this.availableVoices);
            }

            if (this.voice) {
                utterance.voice = this.voice;
            }

            utterance.rate = this.toFiniteNumber(settings.rate, this.defaultRate);
            utterance.pitch = this.toFiniteNumber(settings.pitch, this.defaultPitch);
            utterance.volume = this.toFiniteNumber(settings.volume, this.defaultVolume);
            utterance.lang = settings.lang || (this.voice ? this.voice.lang : "en-US");

            utterance.onstart = function () {
                document.dispatchEvent(
                    new CustomEvent("xiomy:speaking", {
                        detail: { message: message }
                    })
                );
            };

            utterance.onend = function () {
                document.dispatchEvent(
                    new CustomEvent("xiomy:spoken", {
                        detail: { message: message }
                    })
                );
            };

            utterance.onerror = function (event) {
                console.warn("XIOMY speech error:", event.error || event);
            };

            try {
                if (settings.cancelFirst !== false) {
                    this.synth.cancel();
                }
                this.synth.speak(utterance);
                return true;
            } catch (error) {
                console.error("Unable to speak XIOMY message:", error);
                return false;
            }
        }

        stop() {
            if (!this.isSupported || !this.synth) {
                return;
            }
            this.synth.cancel();
        }

        pause() {
            if (!this.isSupported || !this.synth) {
                return;
            }
            if (this.synth.speaking && !this.synth.paused) {
                this.synth.pause();
            }
        }

        resume() {
            if (!this.isSupported || !this.synth) {
                return;
            }
            if (this.synth.paused) {
                this.synth.resume();
            }
        }

        getVoiceInfo() {
            return {
                supported: this.isSupported,
                initialized: this.isInitialized,
                selectedVoice: this.voice
                    ? {
                          name: this.voice.name,
                          lang: this.voice.lang,
                          default: !!this.voice.default,
                          localService: !!this.voice.localService
                      }
                    : null,
                availableCount: this.availableVoices.length
            };
        }

        toFiniteNumber(value, fallback) {
            const parsed = Number(value);
            return Number.isFinite(parsed) ? parsed : fallback;
        }
    }

    class XiomyCommandCenter {
        constructor(voiceEngine) {
            this.voiceEngine = voiceEngine;
            this.recognition = null;
            this.recognitionSupported = false;
            this.isListening = false;
            this.lastTranscript = "";
            this.commandMap = [
                { keywords: ["open crm", "go to crm", "crm"], routeName: "crm", speech: "Opening CRM module." },
                { keywords: ["open hris", "go to hris", "hris"], routeName: "hris", speech: "Opening HRIS module." },
                { keywords: ["open ats", "go to ats", "ats"], routeName: "ats", speech: "Opening ATS module." },
                { keywords: ["open orientation", "go to orientation", "orientation"], routeName: "orientation", speech: "Opening Orientation module." },
                { keywords: ["open sgsst", "go to sgsst", "open s g s s t", "sg-sst", "safety"], routeName: "sgsst", speech: "Opening SG-SST module." },
                { keywords: ["open inventory", "go to inventory", "inventory"], routeName: "inventory", speech: "Opening Inventory module." },
                { keywords: ["open finance", "go to finance", "finance"], routeName: "finance", speech: "Opening Finance module." },
                { keywords: ["open marketing", "go to marketing", "marketing"], routeName: "marketing", speech: "Opening Marketing module." },
                { keywords: ["open calendar", "go to calendar", "calendar"], routeName: "calendar", speech: "Opening Calendar module." },
                { keywords: ["open xiomy", "go to xiomy", "xiomy"], routeName: "xiomy", speech: "Opening XIOMY interface." }
            ];

            this.initializeRecognition();
        }

        initializeRecognition() {
            const SpeechRecognition =
                window.SpeechRecognition || window.webkitSpeechRecognition || null;

            if (!SpeechRecognition) {
                this.recognitionSupported = false;
                return;
            }

            this.recognitionSupported = true;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = "en-US";
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;

            this.recognition.onstart = () => {
                this.isListening = true;
                document.dispatchEvent(new CustomEvent("xiomy:listening"));
            };

            this.recognition.onend = () => {
                this.isListening = false;
                document.dispatchEvent(new CustomEvent("xiomy:stopped-listening"));
            };

            this.recognition.onerror = (event) => {
                this.isListening = false;
                console.warn("XIOMY voice recognition error:", event.error || event);
                document.dispatchEvent(
                    new CustomEvent("xiomy:recognition-error", {
                        detail: { error: event.error || "unknown" }
                    })
                );
            };

            this.recognition.onresult = (event) => {
                const transcript = this.extractTranscript(event);
                this.lastTranscript = transcript;

                document.dispatchEvent(
                    new CustomEvent("xiomy:command-received", {
                        detail: { transcript: transcript }
                    })
                );

                this.processCommand(transcript);
            };
        }

        extractTranscript(event) {
            try {
                const result = event.results[0][0].transcript || "";
                return String(result).trim().toLowerCase();
            } catch (error) {
                return "";
            }
        }

        startListening() {
            if (!this.recognitionSupported || !this.recognition) {
                if (this.voiceEngine) {
                    this.voiceEngine.speak("Voice recognition is not supported in this browser.");
                }
                return false;
            }

            if (this.isListening) {
                return true;
            }

            try {
                this.recognition.start();
                return true;
            } catch (error) {
                console.warn("XIOMY could not start listening:", error);
                return false;
            }
        }

        stopListening() {
            if (!this.recognitionSupported || !this.recognition) {
                return;
            }

            if (this.isListening) {
                this.recognition.stop();
            }
        }

        processCommand(transcript) {
            if (!transcript) {
                if (this.voiceEngine) {
                    this.voiceEngine.speak("I did not catch that. Please repeat your command.");
                }
                return;
            }

            if (transcript.includes("hello xiomy") || transcript.includes("hi xiomy")) {
                if (this.voiceEngine) {
                    this.voiceEngine.speak("Hello Juan Carlos Urbano. I am ready to assist you.");
                }
                return;
            }

            if (transcript.includes("status") || transcript.includes("system status")) {
                if (this.voiceEngine) {
                    this.voiceEngine.speak("All monitored enterprise systems are online.");
                }
                return;
            }

            if (transcript.includes("stop speaking")) {
                if (this.voiceEngine) {
                    this.voiceEngine.stop();
                }
                return;
            }

            if (transcript.includes("pause speaking")) {
                if (this.voiceEngine) {
                    this.voiceEngine.pause();
                }
                return;
            }

            if (transcript.includes("resume speaking")) {
                if (this.voiceEngine) {
                    this.voiceEngine.resume();
                }
                return;
            }

            const matchedCommand = this.findMappedCommand(transcript);

            if (matchedCommand) {
                if (this.voiceEngine) {
                    this.voiceEngine.speak(matchedCommand.speech);
                }

                setTimeout(() => {
                    this.navigateToRoute(matchedCommand.routeName);
                }, 600);

                return;
            }

            if (this.voiceEngine) {
                this.voiceEngine.speak("Command not recognized. Please try again.");
            }
        }

        findMappedCommand(transcript) {
            for (let i = 0; i < this.commandMap.length; i += 1) {
                const command = this.commandMap[i];
                for (let j = 0; j < command.keywords.length; j += 1) {
                    if (transcript.includes(command.keywords[j])) {
                        return command;
                    }
                }
            }
            return null;
        }

        navigateToRoute(routeName) {
            if (!routeName) {
                return;
            }

            const routeRegistry = window.xiomyRoutes || {};
            const url = routeRegistry[routeName];

            if (url) {
                window.location.href = url;
                return;
            }

            const routeElement = document.querySelector('[data-route-name="' + routeName + '"]');
            if (routeElement && routeElement.getAttribute("href")) {
                window.location.href = routeElement.getAttribute("href");
                return;
            }

            console.warn("XIOMY route not found for:", routeName);
        }
    }

    const xiomyVoiceInstance = new XiomyVoice();
    const xiomyCommandCenter = new XiomyCommandCenter(xiomyVoiceInstance);

    window.xiomyVoice = xiomyVoiceInstance;
    window.xiomyCommands = xiomyCommandCenter;

    window.xiomySpeak = function (message, options) {
        return xiomyVoiceInstance.speak(message, options);
    };

    window.xiomyStopSpeaking = function () {
        xiomyVoiceInstance.stop();
    };

    window.xiomyPauseSpeaking = function () {
        xiomyVoiceInstance.pause();
    };

    window.xiomyResumeSpeaking = function () {
        xiomyVoiceInstance.resume();
    };

    window.xiomyGetVoiceInfo = function () {
        return xiomyVoiceInstance.getVoiceInfo();
    };

    window.xiomyStartListening = function () {
        return xiomyCommandCenter.startListening();
    };

    window.xiomyStopListening = function () {
        xiomyCommandCenter.stopListening();
    };

    document.addEventListener("DOMContentLoaded", function () {
        const xiomyWidget = document.getElementById("xiomyWidget");
        const xiomyTalkButtons = document.querySelectorAll("[data-xiomy-speak]");
        const xiomyListenButtons = document.querySelectorAll("[data-xiomy-listen]");
        const xiomyStopButtons = document.querySelectorAll("[data-xiomy-stop]");
        const xiomyStatusTargets = document.querySelectorAll("[data-xiomy-status]");

        registerDefaultRoutes();
        bindWidgetBehavior(xiomyWidget);
        bindSpeakButtons(xiomyTalkButtons);
        bindListenButtons(xiomyListenButtons);
        bindStopButtons(xiomyStopButtons);
        bindStatusIndicators(xiomyStatusTargets);
    });

    function registerDefaultRoutes() {
        if (!window.xiomyRoutes) {
            window.xiomyRoutes = {};
        }

        const anchors = document.querySelectorAll(".module-button[href]");
        anchors.forEach(function (anchor) {
            const titleNode = anchor.querySelector(".module-title");
            if (!titleNode) {
                return;
            }

            const title = String(titleNode.textContent || "").trim().toLowerCase();
            const href = anchor.getAttribute("href");

            if (!href) {
                return;
            }

            if (title === "crm") {
                window.xiomyRoutes.crm = href;
                anchor.setAttribute("data-route-name", "crm");
            } else if (title === "hris") {
                window.xiomyRoutes.hris = href;
                anchor.setAttribute("data-route-name", "hris");
            } else if (title === "ats") {
                window.xiomyRoutes.ats = href;
                anchor.setAttribute("data-route-name", "ats");
            } else if (title === "orientation") {
                window.xiomyRoutes.orientation = href;
                anchor.setAttribute("data-route-name", "orientation");
            } else if (title === "sg-sst") {
                window.xiomyRoutes.sgsst = href;
                anchor.setAttribute("data-route-name", "sgsst");
            } else if (title === "inventory") {
                window.xiomyRoutes.inventory = href;
                anchor.setAttribute("data-route-name", "inventory");
            } else if (title === "finance") {
                window.xiomyRoutes.finance = href;
                anchor.setAttribute("data-route-name", "finance");
            } else if (title === "marketing") {
                window.xiomyRoutes.marketing = href;
                anchor.setAttribute("data-route-name", "marketing");
            } else if (title === "calendar") {
                window.xiomyRoutes.calendar = href;
                anchor.setAttribute("data-route-name", "calendar");
            } else if (title === "xiomy ai") {
                window.xiomyRoutes.xiomy = href;
                anchor.setAttribute("data-route-name", "xiomy");
            }
        });
    }

    function bindWidgetBehavior(widget) {
        if (!widget) {
            return;
        }

        widget.setAttribute("role", "button");
        widget.setAttribute("tabindex", "0");
        widget.setAttribute("aria-label", "XIOMY Assistant");

        widget.addEventListener("dblclick", function () {
            if (window.xiomySpeak) {
                window.xiomySpeak(
                    "Hello Juan Carlos Urbano. XIOMY executive assistant is active and ready."
                );
            }
        });

        widget.addEventListener("contextmenu", function (event) {
            event.preventDefault();
            if (window.xiomyStartListening) {
                window.xiomyStartListening();
            }
        });

        widget.addEventListener("keydown", function (event) {
            if (event.key === "x" || event.key === "X") {
                event.preventDefault();
                if (window.xiomySpeak) {
                    window.xiomySpeak("XIOMY quick voice channel activated.");
                }
            }

            if (event.key === "l" || event.key === "L") {
                event.preventDefault();
                if (window.xiomyStartListening) {
                    window.xiomyStartListening();
                }
            }
        });
    }

    function bindSpeakButtons(buttons) {
        if (!buttons || !buttons.length) {
            return;
        }

        buttons.forEach(function (button) {
            button.addEventListener("click", function () {
                const message = button.getAttribute("data-xiomy-speak") || "";
                if (message && window.xiomySpeak) {
                    window.xiomySpeak(message);
                }
            });
        });
    }

    function bindListenButtons(buttons) {
        if (!buttons || !buttons.length) {
            return;
        }

        buttons.forEach(function (button) {
            button.addEventListener("click", function () {
                if (window.xiomyStartListening) {
                    window.xiomyStartListening();
                }
            });
        });
    }

    function bindStopButtons(buttons) {
        if (!buttons || !buttons.length) {
            return;
        }

        buttons.forEach(function (button) {
            button.addEventListener("click", function () {
                if (window.xiomyStopSpeaking) {
                    window.xiomyStopSpeaking();
                }
            });
        });
    }

    function bindStatusIndicators(targets) {
        if (!targets || !targets.length) {
            return;
        }

        function updateStatus(text) {
            targets.forEach(function (target) {
                target.textContent = text;
            });
        }

        document.addEventListener("xiomy:listening", function () {
            updateStatus("Listening...");
        });

        document.addEventListener("xiomy:stopped-listening", function () {
            updateStatus("Standby");
        });

        document.addEventListener("xiomy:speaking", function () {
            updateStatus("Speaking...");
        });

        document.addEventListener("xiomy:spoken", function () {
            updateStatus("Online");
        });

        document.addEventListener("xiomy:recognition-error", function () {
            updateStatus("Voice Error");
        });
    }
})();