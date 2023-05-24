def show_button(url):
    return f"""<a href="{url}">
                <div class="inline mr-1"> <span class="hbl hbl-view text-2xl text-dark-black/50"></span></div>
            </a>"""


def edit_button(id):
    return f"""<a href="javascript:void(0)" onclick="openUpdateModel({id})">
                <div class="inline mr-1"> <span class="hbl hbl-edit text-2xl text-dark-black/50"></span></div>
            </a>"""


def delete_button(function):
    return f"""<a href="javascript:void(0)" onclick="{function}">
                <div class="inline mr-1"> <span class="hbl hbl-delete text-2xl text-dark-black/50"></span></div>
            </a>"""


def duplicate_button(id):
    return f"""<a href="javascript:void(0)" onclick="duplicateTimelineModal({id})">
                <div class="inline mr-1"> <span class="hbl hbl-description text-2xl text-dark-black/50"></span></div>
            </a>"""
