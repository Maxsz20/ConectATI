class ConectATIRouter:
    route_model_names = {
        'usuario', 'amistad', 'chat', 'comentario',
        'configuracion', 'mensaje', 'notificacion', 'publicacion'
    }

    def db_for_read(self, model, **hints):
        if model.__name__.lower() in self.route_model_names:
            return 'conectati'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__.lower() in self.route_model_names:
            return 'conectati'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        names = self.route_model_names
        if (
            obj1.__class__.__name__.lower() in names or
            obj2.__class__.__name__.lower() in names
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in self.route_model_names:
            return db == 'conectati'
        return db == 'default'
