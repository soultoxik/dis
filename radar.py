from tkinter import *
import random

root = Tk()
root.title('radar')
win_width = 350
win_height = 370
config_string = "{0}x{1}".format(win_width, win_height + 32)
fill_color = "green"

root.geometry(config_string)
cell_size = 20
canvas = Canvas(root, height=win_height)
canvas.pack(fill=BOTH)	

field_height = win_height // cell_size
field_width = win_width // cell_size


canvas1 = Canvas(root, height=win_height)


	
cell_matrix = []
for i in range(field_height):
	for j in range(field_width):
		square = canvas.create_rectangle(2 + cell_size*j, 2 + cell_size*i, cell_size + cell_size*j - 2, cell_size + cell_size*i - 2, fill=fill_color)
								
		cell_matrix.append(square)




def addr(ii,jj):
	if(ii < 0 or jj < 0 or ii >= field_height or jj >= field_width):
		return len(cell_matrix)-1	
	else:
		return ii * (win_width // cell_size) + jj
	
for i in range(field_height):
	for j in range(field_width):
		canvas.itemconfig(cell_matrix[addr(i,j)], state=NORMAL, tags='vis')
		
##random plane		
i=15
j=7		

while (i==15) and (j==7) or (i==16) and (j==7) or (i==17) and (j==7) or (i==15) and (j==8) or (i==16) and (j==8) or (i==17) and (j==8):
	i=random.randint (0,17)
	j=random.randint(0,16)
square = canvas.create_rectangle(2 + cell_size*j, 2 + cell_size*i, cell_size + cell_size*j - 2, cell_size + cell_size*i - 2, fill='red')

##airport 
for i in range(15,18):
	for j in range(7,9):
		square = canvas.create_rectangle(2 + cell_size*j, 2 + cell_size*i, cell_size + cell_size*j - 2, cell_size + cell_size*i - 2, fill='blue')




frame = Frame(root)	


root.mainloop()