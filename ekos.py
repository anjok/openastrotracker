import dbus
import dbus.mainloop.glib
import xml.etree.ElementTree as ET
from gi.repository import GLib
from functools import wraps
from inspect import signature, Parameter

def convert_dbus_value(value):
    if isinstance(value, dbus.String):
        return str(value)
    elif isinstance(value, dbus.Array):
        return [convert_dbus_value(item) for item in value]
    elif isinstance(value, dbus.Dictionary):
        return {convert_dbus_value(k): convert_dbus_value(v) for k, v in value.items()}
    elif isinstance(value, (dbus.Int32, dbus.Int64, dbus.UInt32, dbus.UInt64)):
        return int(value)
    elif isinstance(value, dbus.Double):
        return float(value)
    elif isinstance(value, dbus.Boolean):
        return bool(value)
    elif isinstance(value, dbus.Byte):
        return int(value)
    elif isinstance(value, dbus.ObjectPath):
        return str(value)
    return value

class DBusProxy:
    def __init__(self, clazz, service_name, object_path, interface_name):
        self.bus = dbus.SessionBus()
        self.clazz = clazz
        self.proxy = self.bus.get_object(service_name, object_path)
        self.interface_name = interface_name
        introspectable = dbus.Interface(self.proxy, 'org.freedesktop.DBus.Introspectable')
        xml_data = introspectable.Introspect()
        print(xml_data)
        self._parse_xml(xml_data)
    def _parse_xml(self, xml_data):
        root = ET.fromstring(xml_data)
        for interface in root.findall('interface'):
            if interface.get('name') == self.interface_name:
                self._create_methods(interface)
                self._create_properties(interface)
                self._create_signals(interface)
    def _create_methods(self, interface):
        method_dict = {}
        for method in interface.findall('method'):
            method_name = method.get('name')
            if method_name not in method_dict:
                method_dict[method_name] = {'args': [], 'annotations': {}}
            for arg in method.findall('arg'):
                arg_name = arg.get('name', '')
                direction = arg.get('direction')
                arg_type = arg.get('type')
                method_dict[method_name]['args'].append((arg_name, direction, arg_type))
            for annotation in method.findall('annotation'):
                annotation_name = annotation.get('name')
                annotation_value = annotation.get('value')
                method_dict[method_name]['annotations'][annotation_name] = annotation_value
        for method_name, method_data in method_dict.items():
            params = []
            for arg_name, direction, arg_type in method_data['args']:
                if direction == 'in':
                    params.append(Parameter(arg_name, Parameter.POSITIONAL_OR_KEYWORD))
            sig = signature(lambda *args: None)
            new_sig = sig.replace(parameters=params)
            def create_method(m_name, method_sig):
                @wraps(self.proxy)
                def proxy_method(*args):
                    dbus_method = dbus.Interface(self.proxy, self.interface_name).get_dbus_method(m_name)
                    result = dbus_method(*args)
                    return convert_dbus_value(result)
                proxy_method.__signature__ = method_sig
                return proxy_method
            reflective_method = create_method(method_name, new_sig)
            setattr(self.clazz, method_name, reflective_method)
    def _create_properties(self, interface):
        for prop in interface.findall('property'):
            prop_name = prop.get('name')
            prop_access = prop.get('access')
            def create_property(p_name):
                def get_property(self):
                    return convert_dbus_value(dbus.Interface(self.proxy, 'org.freedesktop.DBus.Properties').Get(self.interface_name, p_name))
                def set_property(self, value):
                    return dbus.Interface(self.proxy, 'org.freedesktop.DBus.Properties').Set(self.interface_name, p_name, value)
                if prop_access == 'read':
                    return property(get_property)
                elif prop_access == 'readwrite':
                    return property(get_property, set_property)
            setattr(self.clazz, prop_name, create_property(prop_name))
    def _create_signals(self, interface):
        if True:
            return
        for signal in interface.findall('signal'):
            signal_name = signal.get('name')
            arg_types = [arg.get('type') for arg in signal.findall('arg')]
            def create_signal_handler(s_name):
                def signal_handler(*args):
                    converted_args = [convert_dbus_value(arg) for arg in args]
                    print(f"Received signal {s_name}: {converted_args}")
                return signal_handler
            signal_handler = create_signal_handler(signal_name)
            self.bus.add_signal_receiver(signal_handler, dbus_interface=self.interface_name, signal_name=signal_name)
if False:
    loop = GLib.MainLoop()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)  # Set the GLib main loop
    loop.run()

class Ekos(DBusProxy):
    def __init__(self):
        super().__init__(Ekos, "org.kde.kstars", "/KStars/Ekos", "org.kde.kstars.Ekos")

class Scheduler(DBusProxy):
    def __init__(self):
        super().__init__(Scheduler, "org.kde.kstars", "/KStars/Ekos/Scheduler", "org.kde.kstars.Ekos.Scheduler")

class Focus(DBusProxy):
    def __init__(self):
        super().__init__(Focus, "org.kde.kstars", "/KStars/Ekos/Focus", "org.kde.kstars.Ekos.Focus")

class Capture(DBusProxy):
    def __init__(self):
        super().__init__(Capture, "org.kde.kstars", "/KStars/Ekos/Capture", "org.kde.kstars.Ekos.Capture")

class Align(DBusProxy):
    def __init__(self):
        super().__init__(Align, "org.kde.kstars", "/KStars/Ekos/Align", "org.kde.kstars.Ekos.Align")

class Guide(DBusProxy):
    def __init__(self):
        super().__init__(Guide, "org.kde.kstars", "/KStars/Ekos/Guide", "org.kde.kstars.Ekos.Guide")

ekos = Ekos()
scheduler = Scheduler()
focus = Focus()
capture = Capture()
align = Align()
guide = Guide()
