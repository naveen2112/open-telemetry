"""
utility function django views
"""


def show_button(url):
    """
    Returns HTML code for a button that redirects to the specified URL
    """
    return f"""<a href="{url}">
                <div class="inline mr-1"> <span class="hbl hbl-view text-2xl 
                    text-dark-black/50"></span></div>
            </a>"""


def edit_button(url):
    """
    Returns HTML code for an edit button with a JavaScript function to
    handle the click event
    """
    return f"""<a href="javascript:void(0)" onclick="openUpdateModel(
                    \'{url}\')">
                <div class="inline mr-1"> <span class="hbl hbl-edit text-2xl 
                    text-dark-black/50"></span></div>
            </a>"""


def holiday_edit_button(url):
    """
    Returns HTML code for an holiday edit button with a JavaScript function to
    handle the click event
    """
    return f"""<a href="javascript:void(0)" onclick="editHoliday(\'{url}\')">
                <div class="inline mr-1"> <span class="hbl hbl-edit text-2xl text-dark-black/50"></span></div>
            </a>"""


def delete_button(function):
    """
    Returns HTML code for a delete button with a JavaScript function to
    handle the click event
    """
    return f"""<a href="javascript:void(0)" onclick="{function}">
                <div class="inline mr-1"> <span class="hbl hbl-delete text-2xl 
                    text-dark-black/50"></span></div>
            </a>"""


def duplicate_button(url):
    """
    Returns HTML code for a duplicate button with a JavaScript function to
    handle the click event
    """
    # TODO :: Need to update the duplicate icon once i got from training team
    return f"""<a href="javascript:void(0)" onclick="duplicateTimelineModal(
                    \'{url}\')">
                <div class="inline mr-1"> <span class="hbl hbl-description text-2xl 
                    text-dark-black/50"></span></div>
            </a>"""


def edit_button_new_page(url):
    """
    Returns HTML code for an edit button that opens the URL in a new page
    """
    return f"""<a href={url}>
                <div class="inline mr-1"> <span class="hbl hbl-edit text-2xl 
                    text-dark-black/50"></span></div>
            </a>"""
