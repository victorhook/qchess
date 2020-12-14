const COMMAND = {
    NEW_GAME: 1,
    GET_MOVES: 10,
};

const IMG_PATH = "/static/images/pieces/";
const IMAGES = createPieceImages();
const COLOR_BORDER = "#332211";
const COLOR_WHITE = '#F7E7C4';
const COLOR_BLACK = '#8F4D27';
const COLOR_SELECT = '#4BE846';
const COLOR_HOVER = '#60B7C9';
const COLOR_HIGHLIGHT = "#3CAD38";
const EMPTY = ".";

const BOARD_WIDTH = 700;
const BOARD_HEIGHT = BOARD_WIDTH;

const csrftoken = getCookie('csrftoken');

let board;
let popupAcitvated = false;
let moveTable;

let player = {color: $("#player").data("color")};
let PLATER = player.color == "white" ? 0 : 1;

$(document).ready(function() {

    const ctx = getGraphcisContext("board");

    board = new Board(ctx.canvas.width, ctx, player.color);
    moveTable = $("#tableMoves");


    /* TODO: Resize board when bigger/smaller?
    window.onresize = (e) => {
        console.log($(window).height(), $(window).width());
    };
    */


    /* -- Modal callbacks -- */

    $("#resignBtn").click((e) => $('#resignModal').modal('show'));
    $("#resignNo").click((e) => $("#resignModal").modal("hide"));
    $("#resignYes").click((e) => sendResign());

    $("#promoteQueen").click(() => modalCallback("queen"));
    $("#promoteRock").click(() => modalCallback("rock"));
    $("#promoteKnight").click(() => modalCallback("knight"));
    $("#promoteBishop").click(() => modalCallback("bishop"));

    $("#winCloseBtn").click((e) => $("#winModal").modal("hide"));
    $("#looseModal").click((e) => $("#looseCloseBtn").modal("hide"));


    sendGetBoard();
    sendGetMoveHistory();
    sendGetStatus();
});

function addMoveToTable(move) {
    moveTable.append('<tr>');
    let row = moveTable.children('tr:last');
    row.append('<td>' + move.moveNbr + '</td>');
    row.append('<td>' + move.moveFrom + '</td>');
    row.append('<td>' + move.moveTo + '</td>');
    moveTable.append('</tr>');
}

function modalCallback(pieceType) {
    sendPromote(pieceType);
    $("#modal").modal("hide");
}

function askForPromotion() {
    $('#modal').modal('show');
}

function getGraphcisContext(id) {
    const ctx = $("#" + id)[0].getContext('2d');
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

function sendGetMoveHistory() {
    sendToServer("get_move_history/", {}, (moveHistory) => {
        updateMoveTable(moveHistory.moves);
    });
}

function sendPromote(pieceType) {
    sendToServer("promotion/", {pieceType: pieceType}, (data) => {
        sendGetBoard();
    });
}

function sendGetStatus() {
    sendToServer("get_status/", {}, (status) => {
        console.log(status);
        if (status.is_check_mate) {
            let winner = sendGetWinner();
        }

        console.log(status);
    });
}

function sendGetWinner() {
    sendToServer("get_winner/", {}, (winner) => {
        if (winner.color == player.color) {
            $("#winModal").modal("show");
        } else {
            $("#looseModal").modal("show");
        }
    });
}


function sendResign() {
    sendToServer("resign/", {}, (status) => {
        $("#resignModal").modal("hide");
        console.log(status);
    });
}

function sendGetAvailableMoves(square, board) {
    sendToServer("get_moves/", {square: square}, (data) => {
        let moves = data.moves.split(' ');
        let squares = data.moves.length > 0 ? moves.map(indexify) : [];
        board.higlight(squares);
    });
}

function sendMakeMove(moveFrom, moveTo) {
    let payload = {moveFrom: moveFrom, moveTo: moveTo};
    sendToServer("make_move/", payload, (moveResult) => {
        sendGetStatus();
        sendGetBoard();
        sendGetMoveHistory();
        if (moveResult.promotion)
            askForPromotion();
    });
}

function updateMoveTable(moveHistory) {
    moveTable.empty();

    if (moveHistory != null) {
        for (let i = 0; i < moveHistory.length; i++) {
            let move = moveHistory[i];
            addMoveToTable({
                moveNbr: i+1,
                moveFrom: move.substring(0, 2),
                moveTo: move.substring(2, 4),
            });

        }
    }

}

function sendGetBoard() {
    sendToServer("get_board/", {}, (data) => {
        board.update(data.board);
    });
}

function sendToServer(url, payload, callback) {
    payload.csrfmiddlewaretoken = csrftoken;
    $.post(location.href + url,
           payload,
           (data) => callback(data));
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
        this.squareSize = size / 9;

        ctx.setStrokeStyle = "black";
        ctx.strokeRect(0, 0, size, size);

        this.squares = [];
        let x, y;
        let xStart = this.squareSize;
        let yStart = 0;

        let color;

        for (var r = 0; r < 8; r++) {
            this.squares.push([]);
            for (var c = 0; c < 8; c++) {
                if ((r % 2 == 0 && c % 2 != 0) || (r % 2 != 0 && c % 2 == 0))
                    color = COLOR_WHITE;
                else
                    color = COLOR_BLACK;

                y = yStart + this.squareSize * r;
                x = xStart + this.squareSize * c;
                this.squares[r].push(
                    new Square(x, y, r, c, this.squareSize, ctx, color));
            }
        }

        this.selected = null;
        this.hover = null;
        this.higlighted = [];

        this.ctx.canvas.addEventListener('mousedown',
                                         (e) => this.onMouseClick(e));
        this.ctx.canvas.onmousemove = (e) => this.onMouseHover(e);


        this.createSideBorder();
        this.createBottomBorder();
    }

    onMouseHover(e) {
        if (popupAcitvated)
            return;
        let pos = getCursorPosition(this.ctx.canvas, e);

        for (var r = 0; r < 8; r++) {
            for (var c = 0; c < 8; c++) {
                let cell = this.squares[r][c];

                if (!this.hitSquare(pos, cell) || this.isHighlighted(cell) ||
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
        }

    onMouseClick(e) {
        if (popupAcitvated)
            return;
        let pos = getCursorPosition(this.ctx.canvas, e);
        for (var row = 0; row < 8; row++) {
            for (var col = 0; col < 8; col++) {

                let square = this.squares[row][col];
                if (!this.hitSquare(pos, square))
                    continue;


                // 1. Click white piece, no prev sel
                // 2. Click white piece, prev sel
                // 2.1 Target is white
                // 2.2 Target is black
                // 2.3 Target is empty
                // 3. Empty square, prev no sel




                if (square.hasPiece()) {

                    if (this.selected != null) {
                        if (square.pieceColor() != this.playerColor) {
                            // Capturing piece
                            let moveFrom = this.getSquare(this.selected.row,
                                                          this.selected.col);
                            let moveTo = this.getSquare(square.row, square.col);
                            sendMakeMove(moveFrom, moveTo);
                            this.deselect(this.selected);
                            this.clearOldHighlights();
                        } else {
                            this.selected.deselect();
                            this.select(square);
                            sendGetAvailableMoves(this.getSquare(row, col), this);
                        }
                    } else {
                        // New click, same color
                        if (square.pieceColor() == this.playerColor) {
                            this.select(square);
                            sendGetAvailableMoves(this.getSquare(row, col), this);
                        } else {
                            this.deselect(square);    // New click, enemy color
                        }
                    }
                } else {
                    if (this.selected != null) {
                        if (this.moveIsValid({row: row, col: col})) {
                            let moveFrom = this.getSquare(this.selected.row,
                                                          this.selected.col);
                            let moveTo = this.getSquare(square.row, square.col);
                            sendMakeMove(moveFrom, moveTo);
                            this.deselect(this.selected);
                            this.clearOldHighlights();
                        } else {
                            this.deselect(this.selected);
                            this.clearOldHighlights();
                        }
                    }
                }

            }
        }
    }

    select(square) {
        square.select();
        this.selected = square;
    }

    deselect(square) {
        square.deselect();
        this.selected = null;
    }

    isSelected(square) {
        return this.selected != null &&
               this.selected.row == square.row &&
               this.selected.col == square.col;
    }

    isHighlighted(compareSquare) {
        for (var i = 0; i < this.higlighted.length; i++) {
            let square = this.higlighted[i];
            if (square.row == compareSquare.row &&
                square.col == compareSquare.col) {
                return true;
            }

        }
        return false;
    }

    clearOldHighlights() {
        this.higlighted.forEach(sq => this.squares[sq.row][sq.col].unhighlight());
        this.higlighted.size = 0;
    }

    higlight(squares) {
        this.clearOldHighlights();
        squares.forEach(sq => {
            let row = this.playerColor == "black" ? sq.row : 7-sq.row;
            this.squares[row][sq.col].highlight();
            this.higlighted.push({row: row, col:sq.col});
        });
    }

    // Checks the highlighted square (the OK moves) and returns if target
    // square is valid.
    moveIsValid(move_to) {
        for (let i = 0; i < this.higlighted.length; i++) {
            let square = this.higlighted[i];
            if (square.row == move_to.row && square.col == move_to.col)
                return true;
        }
        return false;
    }

    getSquare(row, col) {
        if (this.playerColor == "white")
            row = 7 - row;
        row += 1;
        return String.fromCharCode(65+col) + row;
    }


    hitSquare(pos, square) {
        let margin = 2;
        return ((pos.x > square.x+margin && pos.x < square.x2-margin) &&
                (pos.y > square.y+margin && pos.y < square.y2-margin));
    }


    createSideBorder() {
        let x = 0;
        let y = 0;
        let cx = x + (this.squareSize / 2);

        let start = this.playerColor == "black" ? 1 : 8;
        let sign = this.playerColor == "black" ? 1 : -1;

        this.ctx.fillStyle = COLOR_BORDER;
        for (var r = 0; r < 9; r++) {
            this.ctx.strokeStyle = "black";
            let cy = y + (this.squareSize / 2) + this.squareSize * .2;
            this.ctx.strokeRect(x, y, this.squareSize, this.squareSize);
            this.ctx.fillRect(x, y, this.squareSize, this.squareSize);

            if (r < 8) {
                this.ctx.strokeStyle = "white";
                this.ctx.strokeText(start, cx, cy);
                y += this.squareSize;
                start += sign;
            }
        }
    }

    createBottomBorder() {
        let xStart = this.squareSize;
        let y = this.size - this.squareSize
        let cy = y + (this.squareSize / 2) + this.squareSize * .2;

        this.ctx.fillStyle = COLOR_BORDER;

        for (var r = 0; r < 8; r++) {
            let x = xStart + r * this.squareSize;
            let cx = x + (this.squareSize / 2);
            this.ctx.strokeStyle = "black";
            this.ctx.strokeRect(x, y, this.squareSize, this.squareSize);
            this.ctx.fillRect(x, y, this.squareSize, this.squareSize);

            this.ctx.strokeStyle = "white";
            let char = String.fromCharCode(65+r);
            this.ctx.strokeText(char, cx, cy);
        }

    }

    draw() {
        for (var r = 0; r < 8; r++) {
            for (var c = 0; c < 8; c++) {
                this.squares[r][c].draw();
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
                this.squares[row][c].update(board[index++]);
            }
        }
    }
}

class Square {

    constructor(x, y, row, col, size, ctx, color) {
        this.x = x;
        this.y = y;
        this.row = row;
        this.col = col;
        this.piece = null;
        this.image = null;
        this.x2 = this.x + size;
        this.y2 = this.y + size;
        this.size = size;
        this.ctx = ctx;
        this.color = color;

        this.cx = x + (size / 2);
        this.cy = y + (size / 2);

        this.fillCell(color);
    }

    pieceColor() {
        if (this.piece != null) {
            return this.piece < 'a' ? "white" : "black";
        }
        return null;
    }

    hasPiece() {
        return this.piece != null;
    }

    draw() {
        if (this.image != null) {
            //                  image        dx      dy       width     height
            this.ctx.drawImage(this.image, this.x, this.y, this.size, this.size);
        }
    }

    update(symbol) {
        this.piece = symbol;
        let img = IMAGES.get(symbol);

        if (this.piece != EMPTY) {
            this.image = new Image();
            this.image.src = img.src;

            this.image.onload = () => {
                this.draw();
            };
        } else {
            this.image = null;
            this.piece = null;
        }
        this.fillCell(this.last_color);
    }

    fillCell(color) {
        this.ctx.fillStyle = color;
        this.ctx.fillRect(this.x, this.y, this.size, this.size);
        this.draw();
        this.last_color = color;
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
