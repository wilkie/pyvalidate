let player = createSprite(100, 100);
player.x = randomNumber(0, 400);

if (keyWentDown("left")) {
  player.velocityX = -5;
}

if (keyWentDown("right")) {
  player.velocityY = 5;
}

for (let i = 0; i < 4; i++) {
  player.x += 50;
}
