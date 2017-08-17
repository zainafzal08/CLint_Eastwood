#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define TRUE 1
#define FALSE 0

struct renderer{
	int *starIndexes;
	int *starDirections;
	int numStars;
	int lineLength;
};

void progressScreen(struct renderer screen);
void printLine(struct renderer screen);
struct renderer newRenderer(int lineLength, int starNum, int drift);
void step(struct renderer screen);
void destoryRenderer(struct renderer screen);

int main(void){
	struct renderer screen = newRenderer(100, 4 , 0);
	while (1){
		step(screen);
	}
	destoryRenderer(screen);
	return EXIT_SUCCESS;
}


struct renderer newRenderer(int lineLength, int starNum, int drift){
	// generate screen 
	struct renderer screen;
	screen.starIndexes = malloc(sizeof(int)*starNum);
	screen.starDirections = malloc(sizeof(int)*starNum);
	screen.numStars = starNum;
	screen.lineLength = lineLength;
	// set up the stars
	int x = 0;
	while (x < starNum){
		if (x%2 == 0){
			screen.starIndexes[x] = 0 + drift*x;
			screen.starDirections[0] = 1;
		}
		else {
			screen.starIndexes[x] = lineLength-1 - drift*x;
			screen.starDirections[1] = -1;
		}
		x++;
	}
	return screen;
}

void destoryRenderer(struct renderer screen){
	free(screen.starIndexes);
	free(screen.starDirections);
}
void step(struct renderer screen){
	printf("\n");
	printLine(screen);
	progressScreen(screen);
	usleep(20*1000);
}
void progressScreen(struct renderer screen){
	int j = 0;
	int lineLength= screen.lineLength;
	for (j=0; j < screen.numStars; j++){
		if (screen.starIndexes[j] == lineLength-1){
			screen.starDirections[j] = -1;
		}
		if (screen.starIndexes[j] == 0){
			screen.starDirections[j] = 1;
		}
	}
	for (j=0; j < screen.numStars; j++){
		screen.starIndexes[j] = screen.starIndexes[j] + screen.starDirections[j];
	}
}

void printLine(struct renderer screen){
	int i = 0;
	int j = 0;
	for (i=0; i<screen.lineLength; i++){
		int printed = FALSE;
		for (j=0; j<screen.numStars; j++){
			if (i == screen.starIndexes[j] && printed == FALSE){
				printed = TRUE;
				printf("*");
			}
		}
		if (printed == FALSE) printf("-");
	}
}