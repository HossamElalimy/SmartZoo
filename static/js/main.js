const socket = io();

socket.on("animal_info", (data) => {
  document.getElementById("animalName").innerText = data.name;
  document.getElementById("animalImage").src = `/static/${data.image}`;
  document.getElementById("animalFact").innerText = data.fact;

  const sound = document.getElementById("animalSound");
  sound.src = `/static/${data.sound}`;
  sound.play();
});
