import discord

class Next_Button(discord.ui.Button):
	def __init__(self, row: int):
		super().__init__(label="Next",row=row)
		
	async def callback(self, interaction: discord.Interaction):
		assert self.view is not None
		view = self.view
		view.display_next_page()
		
		await interaction.response.edit_message(content="Next Button Pressed. Next page is now displaying.", view=view)


class Prev_Button(discord.ui.Button):
	def __init__(self, row: int):
		super().__init__(label="Prev",row=row)
		
	async def callback(self, interaction: discord.Interaction):
		assert self.view is not None
		view = self.view
		view.display_prev_page()
		
		await interaction.response.edit_message(content="Prev Button Pressed. Previous page is now displaying.", view=view)
		
class Stop_Button(discord.ui.Button):
	def __init__(self, row: int):
		super().__init__(label="STOP",row=row)
		
	async def callback(self, interaction: discord.Interaction):
		assert self.view is not None
		view = self.view
		view.stop()
		view.clear_items()
		
		await interaction.response.edit_message(content="Stop Button Pressed. Interactions have now stopped.", view=view)
	

class Switching_View(discord.ui.View):
	def __init__(self):
		super().__init__()
		
		self.page_index = 0
		self.pages = [
			[Stop_Button(row=2), discord.ui.Button(label="Page 1"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 2"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 3"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 4"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 5"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 6"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 7"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 8"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 9"), Next_Button(row=4)], 
			[Prev_Button(row=0), discord.ui.Button(label="Page 10"), Stop_Button(row=2)]
		]
		
		self.display_page(0)
		
	def display_page(self, page_num):
		assert page_num >= 0 and page_num < len(self.pages)
		for i in self.pages[page_num]:
			self.add_item(i)

	def display_next_page(self):
		self.clear_items()
		self.page_index += 1
		self.display_page(self.page_index)
		
	def display_prev_page(self):
		self.clear_items()
		self.page_index -= 1
		self.display_page(self.page_index)
		
