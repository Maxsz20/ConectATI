class ConectATIRouter:
    route_app_labels = {'app'}  # ← este es el nombre de tu app con los modelos externos

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'conectati'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'conectati'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'conectati'
        return db == 'default'
