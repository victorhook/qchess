const COMMAND = {
    NEW_GAME: 1,
};

const IMG_PATH = "/static/images/pieces/";
const IMAGES = createPieceImages();
const COLOR_BORDER = "#179BB6";
const COLOR_WHITE = '#51492E';
const COLOR_BLACK = '#CABA86';
const COLOR_SELECT = 'green';
const COLOR_HOVER = '#555';


$(document).ready(function() {
    const ctx = $("#board")[0].getContext('2d');
    const csrftoken = getCookie('csrftoken');

    ctx.canvas.width = 400;
    ctx.canvas.height = 400;
    ctx.textAlign = "center";
    let board = new Board(ctx.canvas.width, ctx);

    let b = "RNBQKBNRPPPPPPPP................................pppppppprnbqkbnr"
    board.update(b);

    $('#new_game').click(function() {
        newGame(csrftoken);
    });

});

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

class Board {
    constructor(size, ctx) {
        this.size = size;
        this.ctx = ctx;
        this.cellSize = size / 9;

        ctx.setStrokeStyle = "black";
        ctx.strokeRect(0, 0, size, size);

        this.cells = [];
        let x, y;
        let xStart = this.cellSize;
        let yStart = 0;


        let color;
        for (var r = 0; r < 8; r++) {
            y = yStart + this.cellSize * r;
            for (var c = 0; c < 8; c++) {
                if ((r % 2 == 0 && c % 2 != 0) || (r % 2 != 0 && c % 2 == 0))
                    color = COLOR_WHITE;
                else
                    color = COLOR_BLACK;
                x = xStart + this.cellSize * c;
                this.cells.push(new Cell(x, y, this.cellSize, ctx, color));
            }
        }

        let squares = [];
        for (var i = 0; i < this.cells.length; i++) {
            let cell = this.cells[i];
            squares.push({
                x1: cell.x,
                y1: cell.y,
                x2: cell.x + this.cellSize,
                y2: cell.y + this.cellSize,
            });
        }

        this.selected = null;
        this.hover = null;

        this.ctx.canvas.addEventListener('mousedown', (e) => {
            let pos = getCursorPosition(this.ctx.canvas, e);
            for (var i = 0; i < this.cells.length; i++) {
                let cell = this.cells[i];
                if (this.hitCell(pos, cell)) {

                    if (cell.hasPiece()) {
                        if (this.selected != null) {
                            this.selected.deselect();
                        }
                        this.selected = cell;
                        cell.select();
                    } else {
                        if (this.selected != null) {
                            this.selected.deselect();
                            this.selected = null;
                        }
                    }
                }
            }
        });

        this.ctx.canvas.onmousemove = (e) => {
            let pos = getCursorPosition(this.ctx.canvas, e);
            let found = false;
            for (var i = 0; i < this.cells.length; i++) {
                let cell = this.cells[i];
                if (this.hitCell(pos, cell)) {

                    if (this.selected != cell)
                        cell.hover();

                        if (this.hover != cell && this.hover != null)
                            this.hover.deselect();

                    this.hover = cell;
                    found = true;
                    break;
                }

                if (!found && this.hover != null) {
                    this.hover.deselect();
                    this.hover = null;
                }


            }
            if (this.selected != null)
                this.selected.select();

        };

        this.crateSideBorder();
        this.createBottomBorder();
    }


    hitCell(pos, cell) {
        return ((pos.x > cell.x && pos.x < cell.x2) &&
                (pos.y > cell.y && pos.y < cell.y2));
    }


    crateSideBorder() {
        let x = 0;
        let y = 0;
        let cx = x + (this.cellSize / 2);

        this.ctx.fillStyle = COLOR_BORDER;
        for (var r = 0; r < 8; r++) {
            let cy = y + (this.cellSize / 2);
            this.ctx.strokeRect(x, y, this.cellSize, this.cellSize);
            this.ctx.fillRect(x, y, this.cellSize, this.cellSize);
            let char = String.fromCharCode(65+r);
            this.ctx.strokeText(char, cx, cy);
            y += this.cellSize;
        }
    }

    createBottomBorder() {
        let xStart = this.cellSize;
        let y = this.size - this.cellSize
        let cy = y + (this.cellSize / 2);

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
        for (var i = 0; i < board.length; i++) {
            this.cells[i].draw();
        }
    }

    update(board) {
        this.board = board;
        for (var i = 0; i < board.length; i++) {
            this.cells[i].update(board[i]);
        }
    }
}

class Cell {

    constructor(x, y, size, ctx, color) {
        this.x = x;
        this.y = y;
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

    deselect() {
        this.fillCell(this.color);
    }


}


function newGame(csrftoken) {
    $.post("test/", {
        csrfmiddlewaretoken: csrftoken,
        command: COMMAND.NEW_GAME
    },
        function(data) {
            console.log(data);
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
