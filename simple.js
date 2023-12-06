/*function add(a, b) {
    if (a < 6) {
        return 10;
    }
    return a + b;
}*/

let player = createSprite(100, 100);
player.x = randomNumber(0, 400);

if (player.x > 300) {
  player.isTouching(player);
}

//let x = 5;//add(5, -5);
//let x = add(randomNumber(0, 400), -5);

/*
let x = 1;

if (randomNumber(0, 400) > 200) {
  x = x + 1;
}

x = randomNumber(5, 300) + 100;

*/
