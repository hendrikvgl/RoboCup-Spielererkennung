#-*- coding:utf-8 -*-
def make_ui_proxy(builder):
    class UIProxy(object):
        def __getattr__(self, name):
            result = builder.get_object(name)
            if result is None:
                raise KeyError(name + " not a valid ui-object")
            
            setattr(self, name, result)
            return result

        def get(self, name):
            return getattr(self, name)

        def has(self, name):
            return builder.get_object(name) is not None
        
    return UIProxy()
