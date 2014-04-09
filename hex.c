#include <stdio.h>
#include <intrin.h>
#include <time.h>
#include <stdlib.h>
#define SIZE   13


int update_from_lower(unsigned int mask, unsigned int self,unsigned int lower)
{
	return ((lower | (lower >> 1)) & mask)|self;
}
int update_from_higher(unsigned int mask, unsigned int self,unsigned int higher)
{
	return ((higher | (higher << 1)) & mask)|self;
}
int update_from_self(unsigned int mask, unsigned int same)
{
	return (((same << 1) | same | (same >>1)) & mask);
}

/*rows of the board are represented by integers having 13 significant bits,  
with squares with red pieces are represented by 1 an other squares by zero. This 
function determines if red has won the game by connecting the two red sides. */
int red_wins(unsigned int board[SIZE])
{
	unsigned int reached[SIZE]={board[0]};
	unsigned long stack = 1;
	unsigned going=1;
	unsigned long index;
	unsigned int new_reached;
	while (going){
	going=_BitScanForward(&index,stack);
	stack &= ~(1 << index );
	if (going){
		if (index==0){
			new_reached=update_from_lower(board[index+1],reached[index+1],reached[index]);
			if (new_reached!=reached[index+1]){
				reached[index+1]=new_reached;
				stack |= (1 << (index+1));
			}
		}
		else if (index==SIZE-2){
			new_reached=update_from_higher(board[index-1],reached[index-1],reached[index]);
			if (new_reached!=reached[index-1]){
				reached[index-1]=new_reached;
				stack |= (1 << (index-1));
			}
			new_reached=update_from_self(board[index],reached[index]);
			if (new_reached!=reached[index]){
				reached[index]=new_reached;
				stack |= (1 << index);
			}
			new_reached=update_from_lower(board[index+1],reached[index+1],reached[index]);
			if (new_reached!=0){
				return 1;
			}
		}
		else{
			new_reached=update_from_higher(board[index-1],reached[index-1],reached[index]);
			if (new_reached!=reached[index-1]){
				reached[index-1]=new_reached;
				stack |= (1 << (index-1));
			}
			new_reached=update_from_self(board[index],reached[index]);
			if (new_reached!=reached[index]){
				reached[index]=new_reached;
				stack |= (1 << index);
			}
			new_reached=update_from_lower(board[index+1],reached[index+1],reached[index]);
			if (new_reached!=reached[index+1]){
				reached[index+1]=new_reached;
				stack |= (1 << (index+1));
			}
		}
	}
	else{
	return 0;
	}
	}}
int printboard(unsigned 
			   int board[])
{
	int j;
	int i;
	char row[SIZE+1];
	for(j=0;j<SIZE;j++){
	for(i=0;i<SIZE;i++){
		if ((1<<i) & board[j]){
			row[i]='X';
		}
		else{
			row[i]='O';
		}
	}
	printf("%s\n",row);
	}
	return 0;
}

int load_random(unsigned int trial[SIZE]){
	int i;
	for(i=0;i<SIZE;i++){
	trial[i]=(rand()>>(15-SIZE))&((1<<SIZE) - 1);
	}
	return 0;
}

void add_counts(unsigned int trial[SIZE],unsigned int wins[SIZE*SIZE][SIZE*SIZE],unsigned int tries[SIZE*SIZE][SIZE*SIZE],int a){
	int rownum;
	int colnum;
	int rownumb;
	int colnumb;
	for(rownum=0;rownum<SIZE;rownum++){
		for(colnum=0;colnum<SIZE;colnum++){
			if (trial[rownum] & (1<< colnum)){
				for(rownumb=0;rownumb<SIZE;rownumb++){
					for(colnumb=0;colnumb<SIZE;colnumb++){
						if (!(trial[rownumb] & (1<< colnumb))){
						tries[rownum*13+colnum][rownumb*13+colnumb]++;
						if (a){wins[rownum*13+colnum][rownumb*13+colnumb]++;}
						}
					}
				}
			}
		}
	}
}	

int main()
{
	int blue_min;
	int blue_min_pro;
	int red_max;
	int a;
	int i;
	int j;
	int total=0;
	float ratio_max=0.0;
	float ratio_min=1.0;
	int square_max_row;
	int square_max_column;
	unsigned int wins[SIZE*SIZE][SIZE*SIZE]={{0}};
	unsigned int tries[SIZE*SIZE][SIZE*SIZE]={{0}};
	unsigned int trial[SIZE]={0};
	srand(time(NULL));
	for (j=0;j<1000000;j++){
	load_random(trial);
	a=(red_wins(trial));
	if (a){total+=1;}
	add_counts(trial,wins,tries,a);
	if (j%100000==0 && j ){printf("working... %d \n",j);}
	}
	red_max=0;
	blue_min=0;

	for(i=0;i<SIZE*SIZE;i++){
		ratio_min=1.0;
		for(j=0;j<SIZE*SIZE;j++){
			
			if ((wins[i][j]/(float)tries[i][j])<ratio_min){
				ratio_min=(wins[i][j]/(float)tries[i][j]);
				blue_min_pro=j;
			}}
		if (ratio_min>ratio_max){
		blue_min=blue_min_pro;
		ratio_max=ratio_min;
		red_max=i;
		}
	}
	printf("red moves square %d, blue square  %d \n",red_max,blue_min);
	getchar();
	return 0;
} 

