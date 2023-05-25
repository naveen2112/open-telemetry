def show_btn(url):
    return f"""<a href="{url}">
                <div class="inline mr-1"> <span class="hbl hbl-view text-2xl text-dark-black/50"></span></div>
            </a>"""


def edit_btn(value):
    function = ""
    url = ""
    if type(value) == int:
        function = f"""openUpdateModel({value})"""
        url = "javascript:void(0)"
    else:
        url = value
    return f"""<a href="{url}" onclick="{function}">
                <div class="inline mr-1"> <span class="hbl hbl-edit text-2xl text-dark-black/50"></span></div>
            </a>"""


def delete_btn(function):
    return f"""<a href="javascript:void(0)" onclick="{function}">
                <div class="inline mr-1"> <span class="hbl hbl-delete text-2xl text-dark-black/50"></span></div>
            </a>"""   


def duplicate_btn(id):  
    return f"""<a href="javascript:void(0)" onclick="duplicateTimelineModal({id})">
                <div class="inline mr-1"> <span class="hbl hbl-description text-2xl text-dark-black/50"></span></div>
            </a>"""  

