import esper

from . import components


class Movement(esper.Processor):
    def process(self, dt):
        # I want to rethink this...
        for ent, (model, spatial) in self.world.get_components(components.Model, components.Spatial):
            model.path.reparent_to(spatial.path)
