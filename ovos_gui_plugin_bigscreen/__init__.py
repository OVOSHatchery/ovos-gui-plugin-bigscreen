from ovos_bus_client import Message
from ovos_plugin_manager.templates.gui import GUIExtension
from ovos_utils.log import LOG


class BigscreenExtension(GUIExtension):
    """ Bigscreen Platform Extension: This extension is responsible for managing the Bigscreen
    specific GUI behaviours. The bigscreen extension does not support Homescreens. It includes
    support for Window managment and Window behaviour.

    Args:
        bus: MessageBus instance
        gui: GUI instance
        preload_gui (bool): load GUI skills even if gui client not connected
        permanent (bool): disable unloading of GUI skills on gui client disconnections
    """

    def __init__(self, bus, gui, config, preload_gui=False, permanent=False):
        LOG.info("Bigscreen: Initializing")
        self.interaction_without_idle = True
        self.interaction_skill_id = None
        super().__init__(bus, gui, config, preload_gui, permanent)

    def register_bus_events(self):
        self.bus.on('mycroft.gui.screen.close', self.close_window_by_event)
        self.bus.on('mycroft.gui.force.screenclose', self.close_window_by_force)
        self.bus.on('gui.page.show', self.on_gui_page_show)
        self.bus.on('gui.page_interaction', self.on_gui_page_interaction)
        self.bus.on('gui.namespace.removed', self.close_current_window)

    def on_gui_page_show(self, message):
        override_idle = message.data.get('__idle')
        if override_idle is True:
            self.interaction_without_idle = True
        elif isinstance(override_idle, int) and not (override_idle, bool) and override_idle is not False:
            self.interaction_without_idle = True
        elif (message.data['page']):
            if not isinstance(override_idle, bool) or not isinstance(override_idle, int):
                self.interaction_without_idle = False

    def on_gui_page_interaction(self, message):
        skill_id = message.data.get('skill_id')
        self.interaction_skill_id = skill_id

    def handle_remove_namespace(self, message):
        get_skill_namespace = message.data.get("skill_id", "")
        LOG.info(f"Got Clear Namespace Event In Skill {get_skill_namespace}")
        if get_skill_namespace:
            self.bus.emit(Message("gui.clear.namespace",
                                  {"__from": get_skill_namespace}))

    def close_current_window(self, message):
        skill_id = message.data.get('skill_id')
        LOG.info(f"Bigscreen: Closing Current Window For Skill {skill_id}")
        self.bus.emit(Message('screen.close.idle.event',
                              data={"skill_idle_event_id": skill_id}))

    def close_window_by_event(self, message):
        self.interaction_without_idle = False
        self.bus.emit(Message('screen.close.idle.event',
                              data={"skill_idle_event_id": self.interaction_skill_id}))
        self.handle_remove_namespace(message)

    def close_window_by_force(self, message):
        skill_id = message.data.get('skill_id')
        self.bus.emit(Message('screen.close.idle.event',
                              data={"skill_idle_event_id": skill_id}))
        self.handle_remove_namespace(message)
