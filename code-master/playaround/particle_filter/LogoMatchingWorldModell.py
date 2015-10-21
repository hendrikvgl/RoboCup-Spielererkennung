__author__ = 'sheepy'


class LogoMatchingWorldModel():

    def __init__(self):
        self.logo_positions = {}

    def add_logo_position(self, reference_image, polar_cords):
        if reference_image not in self.logo_positions.keys():
            self.logo_positions[reference_image] = polar_cords




    def put_current_image_in(self, ):