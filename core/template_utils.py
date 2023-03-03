def show_button(url):
    return f'<a type="button" class="btn mb-2 btn-outline-link" href="{url}"><span class="fe fe-eye fe-16"></span></a>'


def edit_button(url):
    return f'<a type="button" class="btn mb-2 btn-outline-link" href="{url}"><span class="fe fe-edit fe-16"></span></a>'


def delete_button(url, name):
    return f'<a type="button" class="btn mb-2 btn-outline-link" href="javascript:void(0);" onclick="commonDelete(\'{url}\', \'{name}\')"><span class="fe fe-trash fe-16"></span></a>'
