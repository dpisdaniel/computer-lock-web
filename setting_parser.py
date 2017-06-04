import os
import string

PROCESS_TUPLE = 0
PATHS_TUPLE = 1
EXTENSION_TUPLE = 2
LIST_ELEMENT = 1
VALID_NAME_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
VALID_PROCESS_CHARS = "-_.()%s%s" % (string.ascii_letters, string.digits)
EMPTY = ''
EXECUTABLE = ".exe"


def parse_settings(settings):
    """
    Parses :param settings and sorts it to a list of 3 tuples. the list's data format is described in :return:
    it also strips each setting from whitespaces before parsing it and drops any setting that isn't either a path, 
    file extension of the form .ext or a process name ending with the .exe extension. all of these don't have to 
    actually exist, they just need to be syntactically correct. 
    
    Important note: this method's valid names and paths aren't the same as most file systems' valid ones. 
    here only ascii encoded names, paths and extensions are accepted while NTFS and most file systems accept UTF-16 
    encoded characters as well. any name, extension or path containing non-ascii characters is just dropped.
    
    For additional information on what is accepted here and what is not, see :meth:`valid_process`, 
    :meth:`valid_path` and :meth:`valid_extension`
    
    :param settings: a string containing the settings seperated by new lines 
    :return: a list of settings sorted into 3 tuples. the first tuple contains the string 'processes' in its first
    element and the list of syntactically correct process names in the second element. the 2nd and 3rd tuples are the 
    same but with 'paths' and 'extensions' in the tuples' first elements respectively
    """
    settings_list = settings.split('\n')
    for i in range(len(settings_list)):
        try:
            settings_list[i] = str(settings_list[i]).strip()  # strips all of our settings from whitespaces
        except UnicodeEncodeError:
            settings_list[i] = EMPTY  # set the current element to be empty since the setting has non-ascii characters
    settings_list = [setting for setting in settings_list if setting is not EMPTY]
    settings_list = validate_settings(settings_list)
    return settings_list


def validate_settings(setting_list):
    """
    Receives the list of settings to validate and sorts them by valid processes, paths, and extensions.
    Returns the sorted list in the formation described in :return:
    
    :param setting_list: the list of setting strings to validate and sort
    :return: the list of settings sorted into 3 tuples. the first tuple contains the string 'processes' in its first
    element and the list of syntactically correct process names in the second element. the 2nd and 3rd tuples are the 
    same but with 'paths' and 'extensions' in the tuples' first elements respectively
    """
    sorted_setting_list = [('processes', []), ('paths', []), ('extensions', [])]
    for setting in setting_list:
        if valid_process(setting):
            sorted_setting_list[PROCESS_TUPLE][LIST_ELEMENT].append(setting)
        elif valid_path(setting):
            sorted_setting_list[PATHS_TUPLE][LIST_ELEMENT].append(setting)
        elif valid_extension(setting):
            sorted_setting_list[EXTENSION_TUPLE][LIST_ELEMENT].append(setting)
    return sorted_setting_list


def valid_process(setting):
    """
    Checks if :param setting is a valid process setting string. A valid process string is a string the ends with 
    .exe and has a valid process name before the extension (the name doesnt have to exist, it just has to make sense)
    
    :param setting: a string containing one setting entry
    :return: True if the setting is a valid process and False otherwise
    """
    if setting.endswith(EXECUTABLE) and setting is not EXECUTABLE:
        for char in setting[:-4]:  # we slice setting to -4 to get whatever is before the extension
            if char not in VALID_PROCESS_CHARS:
                return False
        return True
    return False


def valid_path(setting):
    """
    Checks if :param setting is a valid file path
    a valid file path can either be an absolute path to the file, or just the file name (although it has to begin
    with a forward or backward slash)
    examples: C:/some/path/file.adgf, C:/, /file
    :param setting: a string containing one setting entry
    :return: True if the setting is a valid file path and False otherwise
    """
    try:
        if os.path.isabs(setting) and not setting.endswith(EXECUTABLE):
            return True
        return False
    except Exception as err:
        print err
        return False


def valid_extension(setting):
    """
    Checks if :param: setting is a valid file extension. A valid file extension will have the following syntax:
    ".ext"  the setting must begin with . and be followed by a syntactically correct file extension (it doesnt have
    to exist it just needs to syntactically be correct so it can be a possible extension)
    
    :param setting: a string containing one setting entry
    :return: True if the setting is a valid file extension and False otherwise. 
    """
    try:
        if setting is EXECUTABLE:
            return False
        if setting.startswith('.'):
            for char in setting[1:]:
                if char not in VALID_NAME_CHARS:
                    return False
            return True
        return False
    except Exception as err:
        print err
        return False
