import mido
import obspython as obs
import json

midi_device = ""
device = None
audio_source = []
scene_sources = []
start_note = 0

def connect_to_device(a, b):
    global device
    global midi_device
    device = mido.open_input(midi_device, callback=midi_update)

def midi_update(msg):
    global audio_source 
    global start_note
    global scene_sources
    if (msg.type == "control_change"):
        if (msg.control - 1) < len(audio_source):
            audio_device = audio_source[msg.control - 1]
            audio = obs.obs_get_source_by_name(audio_device)
            if audio is not None:
                volume = float(msg.value) / 127.0
                obs.obs_source_set_volume(audio, volume)
            obs.obs_source_release(audio)
    elif (msg.type == "note_on"):
        index = msg.note - start_note
        if (index < len(scene_sources) and index >= 0):
            scene = obs.obs_get_source_by_name(scene_sources[index])
            obs.obs_frontend_set_current_scene(scene)
            obs.obs_source_release(scene)



def script_unload():
    disconnect_from_device(None, None)

def disconnect_from_device(a, b):
    global device
    global midi_device
    print("attempting disconnect")
    if device is not None:
        device.close()
        device.callback = None
        device = None

def script_properties():
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(props, "source", "midi source",
                                    obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    inputs = mido.get_input_names()
    if inputs is not None:
        for midi in inputs:
            obs.obs_property_list_add_string(p, midi, midi)

    obs.obs_properties_add_button(props, "connect", "Connect", connect_to_device)
    obs.obs_properties_add_button(props, "disconnect", "Disconnect", disconnect_from_device)
    obs.obs_properties_add_text(props, "audio-sources", "Audio Sources", obs.OBS_TEXT_MULTILINE)
    obs.obs_properties_add_text(props, "scene-sources", "Scene Sources", obs.OBS_TEXT_MULTILINE)

    obs.obs_properties_add_int(props, "start-note", "Scene select start note", 0, 108, 1) 
    return props

def value_is_json(json_value):
    try:
        obj = json.loads(json_value)
    except ValueError:
        return False
    return True

def script_update(settings):
    global midi_device
    global audio_source
    global scene_sources
    global start_note
    midi_device = obs.obs_data_get_string(settings, "source")
    start_note = obs.obs_data_get_int(settings, "start-note")
    audio_sources_text = obs.obs_data_get_string(settings, "audio-sources")
    if value_is_json(audio_sources_text):
        audio_source = json.loads(audio_sources_text)
    scene_sources_text = obs.obs_data_get_string(settings, "scene-sources")
    if value_is_json(scene_sources_text):
        scene_sources = json.loads(scene_sources_text)