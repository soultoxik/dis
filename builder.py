

class AirportsBuilder:
	
	def __init__(self):
		self.state = {}
	
	def build(self):
		return self.state
	
	def add(self, id, lat, lon, capacity):
		self.state[id] = {
			'lat': lat,
			'lon': lon,
			'capacity': capacity
		}
		