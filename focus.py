#!/usr/bin/env python2

"""
File: focus.py
Author: Alfred Lee
Created: 2013-10-13

This is a simple little game to train your ability to focus your attention.
"""

import curses
import time
import random


class writer():
    def __init__(self, screen, y, x):
        self.freq = 0.2
        self.growth = 1.5
        self.wait = 1
        self.width = 15
        self.height = 5
        self.screen = screen
        self.y = y
        self.x = x
        self.top = self.y - self.height / 2
        self.left = self.x - self.width / 2
        self.total = 0
        self.caught = 0
        self.missed = 0
        self.reverse = False

    def debug(self, msg):
        self.screen.addstr(self.y * 2 - 1, 0, msg)

    def work(self):
        def timeout(signum, frame):
            '''handle timeout'''
            self.response = -1

        # display pattern
        star = self.refresh()
        self.screen.move(0, 0)
        self.screen.refresh()

        # wait for input
        start = time.time()
        self.screen.timeout(self.wait * 1000)
        self.response = self.screen.getch()

        # fill out the waiting time
        wait = time.time() - start
        if wait < self.wait:
            time.sleep(self.wait - wait)

        # clear screen, log outcome
        self.screen.clear()
        self.check(star)

        self.reverse = not self.reverse  # avoid afterimages
        if self.response in [ord(' '), -1]:
            # next
            self.total += 1
            return 0
        else:
            # quit
            return 1

    def refresh(self):
        '''write pattern to screen'''
        for i, y in enumerate(range(self.height)):
            line = ''.join([random.choice(r'XxY\/')
                            for _ in range(self.width)])
            if self.reverse:
                self.screen.addstr(self.top + i,
                                   self.left,
                                   line,
                                   curses.A_REVERSE)
            else:
                self.screen.addstr(self.top + i,
                                   self.left,
                                   line)
        star = random.random() < self.freq
        if star and self.reverse:
            self.screen.addstr(self.top + random.randint(0, self.height - 1),
                               self.left + random.randint(0, self.width - 1),
                               '*', curses.A_REVERSE)
        elif star:
            self.screen.addstr(self.top + random.randint(0, self.height - 1),
                               self.left + random.randint(0, self.width - 1),
                               '*')
        return star

    def check(self, star):
        '''Check user response/pass'''
        if star and self.response == -1:
            # wrong
            self.screen.addstr((self.top + self.height + 2),
                               self.x - 9, 'MISSED ONE! FOCUS!')
            self.missed += 1
        elif not star and self.response == ord(' '):
            # wrong
            self.screen.addstr((self.top + self.height + 2),
                               self.x - 7, 'NO STAR! FOCUS!')
        elif star and self.response == ord(' '):
            # right
            self.caught += 1
            self.freq /= self.growth

    def print_stats(self):
        self.screen.addstr(self.top,
                           self.left,
                           'total: %d' % self.total)
        self.screen.addstr(self.top + 1,
                           self.left,
                           'caught stars: %d' % self.caught)
        self.screen.addstr(self.top + 2,
                           self.left,
                           'missed stars: %d' % self.missed)

        # wait for input to close
        self.screen.timeout(-1)
        self.screen.getch()


def main(stdscr):
    # initialize
    explanation = '''This is a game to help train your ability to focus
You will see a row of Xs. Occasionally a * will be among the Xs.
When you see a *, press the space bar. Press any other key to quit.
The time between showing a * will increase, straining your attention.
When you are ready to start, press enter.'''
    maxy, maxx = stdscr.getmaxyx()
    w = writer(stdscr, maxy / 2, maxx / 2)

    # splash
    stdscr.addstr(0, 0, explanation)
    stdscr.refresh()
    response = stdscr.getch()
    while response != ord('\n'):
        stdscr.addstr('\nfollow directions!\n')
        response = stdscr.getch()
    stdscr.clear()

    # main loop
    response = w.work()
    while response != 1:
        response = w.work()

    # close out
    w.print_stats()
    time.sleep(1)

if __name__ == '__main__':
    curses.wrapper(main)
