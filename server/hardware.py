class hardwareSet:
    def __init__(self):
        self.__capacity = {}
        self.__availability = {}
        self.__checkedOut = {}

    def initialize_capacity(self, hardware):
        hardware_id = hardware["hardware_id"]
        self.__capacity[hardware_id] = hardware.get("total_capacity", 0)


    def initialize_availability(self, hardware):
        hardware_id = hardware["hardware_id"]
        self.__availability[hardware_id] = hardware.get("available", 0)

    def get_availability(self):
        return self.__availability

    def get_capacity(self):
        return self.__capacity

    def check_out(self, qty, project_ID, hardware_id):
        if project_ID not in self.__checkedOut:
            # initialize with empty mapping; the monolith used {1:0,2:0} — keep flexible
            self.__checkedOut[project_ID] = {}

        available = self.__availability.get(hardware_id, 0)
        if available == 0:
            return -1, 0

        if qty <= available:
            self.__availability[hardware_id] = available - qty
            self.__checkedOut[project_ID][hardware_id] = self.__checkedOut[project_ID].get(hardware_id, 0) + qty
            return 0, self.__availability[hardware_id]
        else:
            # partial checkout
            self.__checkedOut[project_ID][hardware_id] = self.__checkedOut[project_ID].get(hardware_id, 0) + available
            self.__availability[hardware_id] = 0
            return 1, 0

    def check_in(self, qty, project_ID, hardware_id):
        if qty < 0:
            return -4, self.__availability.get(hardware_id, 0)

        if hardware_id not in self.__capacity or hardware_id not in self.__availability:
            return -5, 0

        # Determine how many units can actually be accepted based on capacity
        capacity_limit = self.__capacity[hardware_id] - self.__availability[hardware_id]
        actual_checkin = min(qty, capacity_limit)

        if actual_checkin == 0:
            return -3, self.__availability[hardware_id]

        self.__availability[hardware_id] += actual_checkin

        if project_ID not in self.__checkedOut:
            self.__checkedOut[project_ID] = {}

        self.__checkedOut[project_ID][hardware_id] = self.__checkedOut[project_ID].get(hardware_id, 0) - actual_checkin
        if self.__checkedOut[project_ID][hardware_id] < 0:
            self.__checkedOut[project_ID][hardware_id] = 0

        if actual_checkin < qty:
            return 1, self.__availability[hardware_id]
        return 0, self.__availability[hardware_id]
