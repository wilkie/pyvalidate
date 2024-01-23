// This is preamble code that defines the library functions
// and contains type annotations and hints that help the semantic analysis of
// a program.

class Sprite {
  constructor() {
  }

  /**
   * @param {string} name
   */
  setAnimation(name) {
  }

  /**
   * @param {string} name
   */
  setCollider(name) {
  }

  /**
   * @param {Sprite} sprite
   * @returns {bool}
   */
  isTouching(sprite) {
  }

  /**
   * @param {Sprite} sprite
   */
  displace(sprite) {
  }

  /** @param {number} value */
  set scale(value) {
    this._scale = value;
  }

  /** @returns {number} */
  get scale(value) {
    return this._scale;
  }

  /** @param {number} value */
  set velocityX(value) {
    this._velocityX = value;
  }

  /** @returns {number} */
  get velocityX(value) {
    return this._velocityX;
  }

  /** @param {number} value */
  set velocityY(value) {
    this._velocityY = value;
  }

  /** @returns {number} */
  get velocityY(value) {
    return this._velocityY;
  }

  /** @param {number} value */
  set x(value) {
    this._x = value;
  }

  /** @returns {number} */
  get x(value) {
    return this._x;
  }

  /** @param {number} value */
  set y(value) {
    this._y = value;
  }

  /** @returns {number} */
  get y(value) {
    return this._y;
  }
}

/**
 * @param {number} x
 * @param {number} y
 * @returns {Sprite}
 */
function createSprite(x, y) {
  let sprite = Sprite();
  sprite.x = x;
  sprite.y = y;
  return sprite;
}

/** 
 * @param {string} key - Key that is presssed.
 * @returns {bool}
 */
function keyDown(key) {
}

/**
 */
function drawSprites() {
}

/** 
 * @param {string} color - Color for background.
 */
function background(color) {
}

/**
 * @param {number} number - The new text size.
 */
function textSize(number) {
}

/** 
 * @param {string} color - Color for filling shapes.
 */
function fill(color) {
}

/** 
 * @param {string} string - The text to draw.
 * @param {number} x - The X coordinate for the drawn string.
 * @param {number} y - The Y coordinate for the drawn string.
 */
function text(string, x, y) {
}

/**
 * @param {number} min - The lowest value to randoming generate, inclusive.
 * @param {number} max - The largest value to randoming generate, exclusive.
 * @returns {number}
 */
function randomNumber(min, max) {
  return (Math.random() * (max - min)) + min;
}
