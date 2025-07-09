#include "Snake.h"
#include <ncurses.h>  // Include ncurses.h for KEY_UP, KEY_DOWN, etc.
#include <iostream>

Snake::Snake(int startY, int startX) {
    body.push_back(std::make_pair(startY, startX));
    direction = 'R';  // Start moving right
    growing = false;
}

void Snake::move() {
    std::pair<int, int> newHead = body.front();

    switch (direction) {
        case 'U': newHead.first--; break;    // Up decreases Y
        case 'D': newHead.first++; break;    // Down increases Y
        case 'L': newHead.second--; break;   // Left decreases X
        case 'R': newHead.second++; break;   // Right increases X
    }

    body.insert(body.begin(), newHead);
    if (!growing) {
        body.pop_back();
    }
    growing = false;
}

void Snake::grow() {
    growing = true;
}

bool Snake::checkCollision(int maxY, int maxX) {
    std::pair<int, int> head = body.front();

    // Check wall collision
    if (head.first <= 0 || head.first >= maxY - 1 ||
        head.second <= 0 || head.second >= maxX - 1)
        return true;

    // Check self collision
    for (std::size_t i = 1; i < body.size(); i++) {
        if (head == body[i])
            return true;
    }

    return false;
}

std::pair<int, int> Snake::getHead() const {
    return body.front();
}

const std::vector<std::pair<int, int>>& Snake::getBody() const {
    return body;
}

void Snake::setDirection(int newDirection) {
    char dir = direction;

    // Debug: Print the key code
    std::cout << "Key pressed: " << newDirection << std::endl;

    // Handle arrow keys only
    if (newDirection == KEY_UP) dir = 'U';
    else if (newDirection == KEY_DOWN) dir = 'D';
    else if (newDirection == KEY_LEFT) dir = 'L';
    else if (newDirection == KEY_RIGHT) dir = 'R';

    // Prevent 180-degree turns
    if ((dir == 'U' && direction != 'D') ||
        (dir == 'D' && direction != 'U') ||
        (dir == 'L' && direction != 'R') ||
        (dir == 'R' && direction != 'L')) {
        direction = dir;
    }

    // Debug: Print the new direction
    std::cout << "New direction: " << direction << std::endl;
}

bool Snake::collidesWith(int y, int x) const {
    for (const auto& segment : body) {
        if (segment.first == y && segment.second == x)
            return true;
    }
    return false;
}
