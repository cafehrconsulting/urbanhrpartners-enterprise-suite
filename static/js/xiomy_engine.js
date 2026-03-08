let scene, camera, renderer, avatar

init()

function init(){

scene = new THREE.Scene()

camera = new THREE.PerspectiveCamera(
75,
window.innerWidth/window.innerHeight,
0.1,
1000
)

renderer = new THREE.WebGLRenderer({alpha:true})
renderer.setSize(500,700)

document
.getElementById("xiomy-avatar")
.appendChild(renderer.domElement)

camera.position.z = 2

const light = new THREE.HemisphereLight(0xffffff,0x444444)
scene.add(light)

loadAvatar()

animate()

}

function loadAvatar(){

const loader = new THREE.GLTFLoader()

loader.load(
"/static/xiomy/xiomy_idle.glb",

function(gltf){

avatar = gltf.scene
avatar.scale.set(1.2,1.2,1.2)

scene.add(avatar)

})

}

function animate(){

requestAnimationFrame(animate)

renderer.render(scene,camera)

}

function startListening(){

document.getElementById("xiomy-status").innerText =
"Listening..."

recognizeSpeech()

}

function recognizeSpeech(){

const recognition = new webkitSpeechRecognition()

recognition.lang = "en-US"

recognition.start()

recognition.onresult = function(event){

let command = event.results[0][0].transcript

document.getElementById("xiomy-status").innerText =
"You said: " + command

processCommand(command)

}

}

function processCommand(command){

if(command.includes("CRM")){

speak("Opening the CRM module")

window.location.href="/crm"

}

if(command.includes("HRIS")){

speak("Opening the HRIS module")

window.location.href="/hris"

}

}

function speak(text){

const speech = new SpeechSynthesisUtterance(text)

speech.rate = 1

speech.pitch = 1

speech.lang = "en-US"

speechSynthesis.speak(speech)

}