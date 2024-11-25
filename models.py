class User:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        user = self.get_user()
        self.name = user["name"]
        self.email = user["email"]
        self.center = user["center"]["name"]
        self.province = user["province"]["name"]
        self.zone = user["zone"]["name"]
        self.institution = user["institution"]["name"]
        self.usertype = user["usertype"]["name"]
        self.resource = user["resource"]["name"]

    def get_user(self):
        import requests
        response = requests.get("http://ncprac.com/api/me", headers={"Authorization": "Bearer " + self.bearer_token})
        return response.json()
    
    def availability(self, is_available=None):
        if is_available==None:
            import requests
            response = requests.get("http://ncprac.com/api/user/availability", headers={"Authorization": "Bearer " + self.bearer_token})
            return response.json()['is_available']
        else:
            import requests
            response = requests.put("http://ncprac.com/api/user/availability", headers={"Authorization": "Bearer " + self.bearer_token}, data={"is_available": is_available})
            return response.json()['message']
        
    def routes(self):
        import requests
        response = requests.get("http://ncprac.com/api/routes/available", headers={"Authorization": "Bearer " + self.bearer_token})
        return [Route(route) for route in response.json()['routes']]
    
    def get_route(self, route_id):
        import requests
        response = requests.get(f"http://ncprac.com/api/routes/{route_id}", headers={"Authorization": "Bearer " + self.bearer_token})
        return Route(response.json()['route'])
    
    def start_route(self, route_id):
        import requests
        response = requests.put(f"http://ncprac.com/api/routes/{route_id}/start", headers={"Authorization": "Bearer " + self.bearer_token})

    def inform_pickup(self, route_id):
        import requests
        response = requests.put(f"http://ncprac.com/api/routes/{route_id}/informPickedUp", headers={"Authorization": "Bearer " + self.bearer_token})

    def end_route(self, route_id):
        import requests
        response = requests.put(f"http://ncprac.com/api/routes/{route_id}/finish", headers={"Authorization": "Bearer " + self.bearer_token})
        self.availability(True)

    def send_location(self, route_id, latitude, longitude):
        import requests
        response = requests.post(f"http://ncprac.com/api/routes/{route_id}/location", headers={"Authorization": "Bearer " + self.bearer_token}, data={"latitude": latitude, "longitude": longitude})

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', center='{self.center}', province='{self.province}', zone='{self.zone}', institution='{self.institution}', usertype='{self.usertype}', resource='{self.resource}')>"
    
    #string to show in telegram
    def __str__(self):
        return f"Nombre: {self.name}\nEmail: {self.email}\nCentro: {self.center}\nProvincia: {self.province}\nZona: {self.zone}\nInstitucion: {self.institution}\nTipo de usuario: {self.usertype}\nRecurso: {self.resource}"
    

class Route:
    def __init__(self,payload):
        self.id = payload['id']
        self.resource_id = payload['resource_id']
        self.user_id = payload['user_id']
        self.start_address = payload['start_address']
        self.start_latitude = payload['start_latitude']
        self.start_longitude = payload['start_longitude']
        self.emergency_address = payload['emergency_address']
        self.emergency_latitude = payload['emergency_latitude']
        self.emergency_longitude = payload['emergency_longitude']
        self.destination_address = payload['destination_address']
        self.start_time = payload['start_time']
        self.pickup_time = payload['pickup_time']
        self.end_time = payload['end_time']
        self.destination_latitude = payload['destination_latitude']
        self.destination_longitude = payload['destination_longitude']
        self.instructions = payload['instructions']
        self.created_at = payload['created_at']
        self.updated_at = payload['updated_at']
        self.resource = payload['resource']
    
    def __repr__(self):
        return f"<Route(id='{self.id}', resource_id='{self.resource_id}', user_id='{self.user_id}', start_address='{self.start_address}', start_latitude='{self.start_latitude}', start_longitude='{self.start_longitude}', emergency_address='{self.emergency_address}', emergency_latitude='{self.emergency_latitude}', emergency_longitude='{self.emergency_longitude}', destination_address='{self.destination_address}', start_time='{self.start_time}', pickup_time='{self.pickup_time}', end_time='{self.end_time}', destination_latitude='{self.destination_latitude}', destination_longitude='{self.destination_longitude}', instructions='{self.instructions}', created_at='{self.created_at}', updated_at='{self.updated_at}', resource='{self.resource}')>"
    
    def __str__(self) -> str:
        return f"""ID: {self.id}
Recurso: {self.resource['name']}
Direccion de inicio: {self.start_address}
Direccion de emergencia: {self.emergency_address}
Direccion de destino: {self.destination_address}
Instrucciones: {self.instructions}"""+f"\n{f'Hora de inicio: {self.start_time}' if self.start_time else ''}\n{f'Hora de recogida: {self.pickup_time}' if self.pickup_time else ''}\n{f'Hora de finalizacion: {self.end_time}' if self.end_time else ''}"