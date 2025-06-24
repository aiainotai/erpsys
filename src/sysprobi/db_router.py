class SysproRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'swkd':
            return 'SWKD'
        elif model._meta.app_label == 'wkmm':
            return 'WKMM'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['swkd', 'wkmm']:
            return None  # Disallow writes
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ['swkd', 'wkmm']:
            return False  # Never allow migrations
        return db == 'default'
