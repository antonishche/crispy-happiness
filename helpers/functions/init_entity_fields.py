def init_entity_fields(entity, settings):
    for key, value in settings.items():
        setattr(entity, key, value)