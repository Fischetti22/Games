#ifndef SNAKE_H
#define SNAKE_H

#include <vector>
#include <utility>

class Snake {
    std::vector<std::pair<int, int>> body;
    char direction;
    bool growing;

public:
    Snake(int startY, int startX);
    void move();
    void grow();
    bool checkCollision(int maxY, int maxX);
    std::pair<int, int> getHead() const;
    const std::vector<std::pair<int, int>>& getBody() const;
    void setDirection(int newDirection);
    bool collidesWith(int y, int x) const;
};

#endif

