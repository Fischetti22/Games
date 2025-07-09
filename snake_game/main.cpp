#include <ncurses.h>
#include <cstdlib>
#include <ctime>
#include "Snake.h"

void generateFood(int& foodY, int& foodX, const Snake& snake, int maxY, int maxX) {
    do {
        foodY = rand() % (maxY-2) + 1;
        foodX = rand() % (maxX-2) + 1;
    } while (snake.collidesWith(foodY, foodX));
}

int main() {
    // Initialize ncurses
    initscr();
    noecho();
    curs_set(0);
    keypad(stdscr, TRUE);
    timeout(100);
    
    // Get screen dimensions
    int maxY, maxX;
    getmaxyx(stdscr, maxY, maxX);
    
    // Initialize game state
    srand(time(0));
    Snake snake(maxY/2, maxX/2);
    int foodY, foodX;
    generateFood(foodY, foodX, snake, maxY, maxX);
    int score = 0;
    bool gameOver = false;
    
    // Game loop
    while (!gameOver) {
        // Clear screen
        clear();
        
        // Draw border
        for (int i = 0; i < maxX; i++) {
            mvaddch(0, i, '-');
            mvaddch(maxY-1, i, '_');
        }
        for (int i = 0; i < maxY; i++) {
            mvaddch(i, 0, '|');
            mvaddch(i, maxX-1, '|');
        }
        
        // Draw score
        mvprintw(0, 2, "Score: %d", score);
        
        // Draw food
        mvaddch(foodY, foodX, '*');
        
        // Draw snake
        for (const auto& segment : snake.getBody()) {
            mvaddch(segment.first, segment.second, 'o');
        }
        
        // Get input
        // Get input
        int ch = getch();
        if (ch != ERR) {  // Only process input if a key was pressed
            switch(ch) {
        	case KEY_UP: snake.setDirection(KEY_UP); break;
        	case KEY_DOWN: snake.setDirection(KEY_DOWN); break;
        	case KEY_LEFT: snake.setDirection(KEY_LEFT); break;
        	case KEY_RIGHT: snake.setDirection(KEY_RIGHT); break;
        	case 'q': gameOver = true; break;
    }
}
        
        // Move snake
        snake.move();
        
        // Check collisions
        if (snake.checkCollision(maxY, maxX)) {
            gameOver = true;
            break;
        }
        
        // Check if food eaten
        if (snake.getHead().first == foodY && snake.getHead().second == foodX) {
            snake.grow();
            score += 10;
            generateFood(foodY, foodX, snake, maxY, maxX);
        }
        
        refresh();
    }
    
    // Game over screen
    clear();
    mvprintw(maxY/2, maxX/2 - 5, "GAME OVER!");
    mvprintw(maxY/2 + 1, maxX/2 - 7, "Final Score: %d", score);
    refresh();
    timeout(-1);
    getch();
    
    // Clean up
    endwin();
    return 0;
}

