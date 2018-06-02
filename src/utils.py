def append_variable_to_url(URL, var_dict):
    '''
    Properly format string to append variable to URL
    :param var_dict:
    :return: URL variables string
    '''
    var_string = ""

    for key in var_dict:
        if var_string == "":
            var_string = var_string + "?" + key + "=" + var_dict[key]
        else:
            var_string = var_string + "&" + key + "=" + var_dict[key]

    return URL+var_string


def download_img_from_url(img_url, save_img_path):
    '''
    Download an image from a URL and save file as save_img_path
    :param img_url: string, URL to image
    :param save_path: string, path to the file to save
    :return:
    '''
    import requests

    try:
        img_data = requests.get(img_url).content

        with open(save_img_path, 'wb') as handler:
            handler.write(img_data)
    except FileNotFoundError:
        pass