const COMMAND = {
    NEW_GAME: 1,
    GET_MOVES: 10,
};

const IMG_PATH = "/static/images/pieces/";
const IMAGES = createPieceImages();
const COLOR_BORDER = "#179BB6";
const COLOR_WHITE = '#51492E';
const COLOR_BLACK = '#CABA86';
const COLOR_SELECT = 'green';
const COLOR_HOVER = '#555';
const COLOR_HIGHLIGHT = "purple";

const BOARD_WIDTH = 400;
const BOARD_HEIGHT = 400;

const csrftoken = getCookie('csrftoken');

$(document).ready(function() {

    let player = {
        color: $("#player").data("color"),
    };

    const ctx = getGraphcisContext();
    let board = new Board(ctx.canvas.width, ctx, player.color);
    let b = "RNBQKBNRPPPPPPPP................................pppppppprnbqkbnr"
    board.update(b);

});

function getGraphcisContext() {
    const ctx = $("#board")[0].getContext('2d');
    ctx.canvas.width = BOARD_WIDTH;
    ctx.canvas.height = BOARD_HEIGHT;
    ctx.textAlign = "center";
    ctx.font = "20px Arial";
    return ctx;
}

function getCursorPosition(canvas, event) {
    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    return {x: x, y: y};
}

function createPieceImages() {
    let images = new Map();
    images.set("P", createImage("wpawn.svg"));
    images.set("N", createImage("wknight.svg"));
    images.set("B", createImage("wbishop.svg"));
    images.set("R", createImage("wrock.svg"));
    images.set("Q", createImage("wqueen.svg"));
    images.set("K", createImage("wking.svg"));
    images.set("p", createImage("bpawn.svg"));
    images.set("n", createImage("bknight.svg"));
    images.set("b", createImage("bbishop.svg"));
    images.set("r", createImage("brock.svg"));
    images.set("q", createImage("bqueen.svg"));
    images.set("k", createImage("bking.svg"));
    return images;
}

function createImage(src) {
    let img = new Image();
    img.src = IMG_PATH + src;
    return img;
}

function sendGetAvailableMoves(square, board) {
    $.post(location.href + "get_moves/", {
        csrfmiddlewaretoken: csrftoken,
        square: square
    },
        (data) => {
            let moves = data.moves.split(' ');
            let squares = data.moves.length > 0 ? moves.map(indexify) : [];
            board.higlight(squares);
    });
}

function indexify(square) {
    let row = square.charCodeAt(1) - 49;
    let col = square.charCodeAt(0) - 65;
    return {row: row, col: col};
}

class Board {
    constructor(size, ctx, playerColor) {
        this.size = size;
        this.ctx = ctx;
        this.playerColor = playerColor;
        this.cellSize = size / 9;

        ctx.setStrokeStyle = "black";
        ctx.strokeRect(0, 0, size, size);

        this.cells = [];
        let x, y;
        let xStart = this.cellSize;
        let yStart = 0;

        let color;

        for (var r = 0; r < 8; r++) {
            this.cells.push([]);
            for (var c = 0; c < 8; c++) {
                if ((r % 2 == 0 && c % 2 != 0) || (r % 2 != 0 && c % 2 == 0))
                    color = COLOR_WHITE;
                else
                    color = COLOR_BLACK;

                y = yStart + this.cellSize * r;
                x = xStart + this.cellSize * c;
                this.cells[r].push(
                    new Cell(x, y, r, c, this.cellSize, ctx, color));
            }
        }

        this.selected = null;
        this.hover = null;
        this.higlighted = [];

        this.ctx.canvas.addEventListener('mousedown', (e) => {
            let pos = getCursorPosition(this.ctx.canvas, e);
            for (var r = 0; r < 8; r++) {
                for (var c = 0; c < 8; c++) {

                    let cell = this.cells[r][c];
                    if (!this.hitCell(pos, cell))
                        continue;

                    if (this.selected != null) {
                        let moveFrom = this.getSquare(this.selected.row,
                                                      this.selected.col);
                        let moveTo = this.getSquare(cell.row, cell.col);

                        // * TODO:
                        // SEND MOVETO

                        this.selected.deselect();
                        this.clearOldHighlights();
                        this.selected = null;

                    } else if(cell.hasPiece()) {
                        sendGetAvailableMoves(this.getSquare(r, c), this);
                        cell.select();
                        this.selected = cell;
                    }
                }
            }
        });



        this.ctx.canvas.onmousemove = (e) => {
            let pos = getCursorPosition(this.ctx.canvas, e);

            for (var r = 0; r < 8; r++) {
                for (var c = 0; c < 8; c++) {
                    let cell = this.cells[r][c];

                    if (!this.hitCell(pos, cell) || this.isHighlighted(cell) ||
                        this.isSelected(cell) )
                        continue;

                    if (this.hover != null && this.hover != this.selected)
                        this.hover.unHover();

                    cell.hover();
                    this.hover = cell;
                    return;
                }
            }

            // If mouse is out of any hover-hit, we remove the last-hover square
            if (this.hover != null && this.hover != this.selected &&
                !this.isHighlighted(this.hover)) {
                    this.hover.unHover();
                    this.hover = null;
                }
        };

        this.crateSideBorder();
        this.createBottomBorder();
    }

    isSelected(cell) {
        return this.selected != null &&
               this.selected.row == cell.row &&
               this.selected.col == cell.col;
    }

    isHighlighted(cell) {
        for (var i = 0; i < this.higlighted.length; i++) {
            let square = this.higlighted[i];
            if (square.row == cell.row && square.col == cell.col) {
                return true;
            }

        }
        return false;
    }

    clearOldHighlights() {
        this.higlighted.forEach(sq => this.cells[sq.row][sq.col].unhighlight());
        this.higlighted.size = 0;
    }

    higlight(squares) {
        this.clearOldHighlights();
        squares.forEach(sq => {
            let row = this.playerColor == "black" ? sq.row : 7-sq.row;
            this.cells[row][sq.col].highlight();
            this.higlighted.push({row: row, col:sq.col});
        });
    }

    getSquare(row, col) {
        if (this.playerColor == "white")
            row = 7 - row;
        row += 1;
        return String.fromCharCode(65+col) + row;
    }


    hitCell(pos, cell) {
        let margin = 2;
        return ((pos.x > cell.x+margin && pos.x < cell.x2-margin) &&
                (pos.y > cell.y+margin && pos.y < cell.y2-margin));
    }


    crateSideBorder() {
        let x = 0;
        let y = 0;
        let cx = x + (this.cellSize / 2);

        let start = this.playerColor == "black" ? 1 : 8;
        let sign = this.playerColor == "black" ? 1 : -1;

        this.ctx.fillStyle = COLOR_BORDER;
        for (var r = 0; r < 8; r++) {
            let cy = y + (this.cellSize / 2) + this.cellSize * .2;
            this.ctx.strokeRect(x, y, this.cellSize, this.cellSize);
            this.ctx.fillRect(x, y, this.cellSize, this.cellSize);

            this.ctx.strokeText(start, cx, cy);
            y += this.cellSize;
            start += sign;
        }
    }

    createBottomBorder() {
        let xStart = this.cellSize;
        let y = this.size - this.cellSize
        let cy = y + (this.cellSize / 2) + this.cellSize * .2;

        this.ctx.fillStyle = COLOR_BORDER;

        for (var r = 0; r < 8; r++) {
            let x = xStart + r * this.cellSize;
            let cx = x + (this.cellSize / 2);

            this.ctx.strokeRect(x, y, this.cellSize, this.cellSize);
            this.ctx.fillRect(x, y, this.cellSize, this.cellSize);
            let char = String.fromCharCode(65+r);
            this.ctx.strokeText(char, cx, cy);
        }

    }

    draw() {
        for (var r = 0; r < 8; r++) {
            for (var c = 0; c < 8; c++) {
                this.cells[r][c].draw();
            }
        }
    }

    update(board) {
        this.board = board;
        let row;
        let index = 0;
        for (var r = 0; r < 8; r++) {
            for (var c = 0; c < 8; c++) {
                row = this.playerColor == "black" ? r : 7-r;
                this.cells[row][c].update(board[index++]);
            }
        }
    }
}

class Cell {

    constructor(x, y, row, col, size, ctx, color) {
        this.x = x;
        this.y = y;
        this.row = row;
        this.col = col;
        this.x2 = this.x + size;
        this.y2 = this.y + size;
        this.size = size;
        this.ctx = ctx;
        this.color = color;

        this.cx = x + (size / 2);
        this.cy = y + (size / 2);

        ctx.strokeStyle = "black";
        ctx.strokeRect(x, y, x+size, y+size);
        ctx.fillStyle = color;
        ctx.fillRect(x, y, x+size, y+size);

    }

    hasPiece() {
        return this.image != null;
    }

    draw() {
        if (this.image != null)
            this.ctx.drawImage(this.image, this.x, this.y);
    }

    update(symbol) {
        let img = IMAGES.get(symbol);

        if (typeof img === 'object') {
            this.image = new Image();
            this.image.src = img.src;
            this.image.onload = () => this.ctx.drawImage(this.image, this.x, this.y);
            this.ctx.strokeText('A', this.cx, this.cy);
        } else
            this.image = null;
    }

    fillCell(color) {
        this.ctx.strokeStyle = "black";
        this.ctx.strokeRect(this.x, this.y, this.size, this.size);
        this.ctx.fillStyle = color;
        this.ctx.fillRect(this.x, this.y, this.size, this.size);
        this.draw();
    }

    select() {
        this.fillCell(COLOR_SELECT);
    }

    hover() {
        this.fillCell(COLOR_HOVER);
    }

    unHover() {
        this.deselect();
    }

    deselect() {
        this.fillCell(this.color);
    }

    highlight() {
        this.fillCell(COLOR_HIGHLIGHT);
    }

    unhighlight() {
        this.deselect();
    }


}


function newGame(csrftoken, player) {
    $.post("test/", {
        csrfmiddlewaretoken: csrftoken,
        command: COMMAND.NEW_GAME
    },
        (data) => {

    });
}

function getCookie(name) {
    /* Taken from django docs https://docs.djangoproject.com/en/3.1/ref/csrf/ */
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
