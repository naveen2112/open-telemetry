def show_btn(url):
    return f"""<a href="{url}">  
                    <div class="inline mr-1">
                        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="24px" height="24px" viewBox="0 0 24 24" version="1.1">
                            <title>View</title>
                            <g id="Final---User-Profile" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" fill-opacity="0.5">
                                <g id="UserProfile---list" transform="translate(-1381.000000, -348.000000)" fill="#020C2D">
                                    <g id="Group-3-Copy" transform="translate(120.000000, 340.000000)">
                                        <g id="Group-2" transform="translate(1227.000000, 8.000000)">
                                            <g id="delete" transform="translate(34.000000, 0.000000)">
                                                <path d="M12,5 C14.3377917,5 17.4880416,6.77941246 21.5915818,10.3094407 L21.5915818,10.3094407 L22.3044104,10.9317319 L22.6678778,11.2557291 C23.1107074,11.6531059 23.1107074,12.3468941 22.6678778,12.7442709 C22.5459351,12.8536973 22.4247804,12.9616966 22.3044104,13.0682681 L22.3044104,13.0682681 L21.5915818,13.6905593 C17.4880416,17.2205875 14.3377917,19 12,19 C9.66220831,19 6.51195837,17.2205875 2.40841822,13.6905593 L2.40841822,13.6905593 L1.69558956,13.0682681 L1.3321222,12.7442709 C0.889292601,12.3468941 0.889292601,11.6531059 1.3321222,11.2557291 C1.45406494,11.1463027 1.57521963,11.0383034 1.69558956,10.9317319 L1.69558956,10.9317319 L2.40841822,10.3094407 C6.51195837,6.77941246 9.66220831,5 12,5 Z M12,7 C10.2723367,7 7.45480542,8.60647029 3.68726161,11.8480079 L3.68726161,11.8480079 L3.512,12 L4.02745457,12.4424364 C4.59005994,12.9189918 5.13071835,13.3579622 5.64894201,13.7594473 L5.64894201,13.7594473 L6.26001049,14.2232428 C8.66095992,16.0065042 10.5405169,16.9270231 11.8447343,16.9958302 L11.8447343,16.9958302 L12,17 C13.7276633,17 16.5451946,15.3935297 20.3127384,12.1519921 L20.3127384,12.1519921 L20.487,12 L19.9725454,11.5575636 C19.4099401,11.0810082 18.8692816,10.6420378 18.351058,10.2405527 L18.351058,10.2405527 L17.7399895,9.77675716 C15.3390401,7.99349578 13.4594831,7.07297694 12.1552657,7.00416977 L12.1552657,7.00416977 Z M12,10 C13.1045695,10 14,10.8954305 14,12 C14,13.1045695 13.1045695,14 12,14 C10.8954305,14 10,13.1045695 10,12 C10,10.8954305 10.8954305,10 12,10 Z" id="Combined-Shape"></path>
                                            </g>
                                        </g>
                                    </g>
                                </g>
                            </g>
                        </svg>
                    </div>
                </a>"""


def edit_btn(id):
    return f"""<a href="#" onclick="openUpdateModel({id})" tabindex="-1">
                    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="24px" height="24px" viewBox="0 0 24 24" version="1.1">
                        <title>Edit</title>
                        <g id="Final---User-Profile" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" fill-opacity="0.5">
                            <g id="UserProfile---edit" transform="translate(-1347.000000, -228.000000)" fill="#020C2D">
                                <g id="Group-3" transform="translate(120.000000, 220.000000)">
                                    <g id="edit" transform="translate(1227.000000, 8.000000)">
                                        <path id="Combined-Shape" d="M14,9 L14,17.3944487 C14,17.7892987 13.8831239,18.1753141 13.6641006,18.5038491 L12,21 L10.3358994,18.5038491 C10.1168761,18.1753141 10,17.7892987 10,17.3944487 L10,9 L14,9 Z M12,3 C13.1045695,3 14,3.8954305 14,5 L14,7 L10,7 L10,5 C10,3.8954305 10.8954305,3 12,3 Z" transform="translate(12.000000, 12.000000) rotate(30.000000) translate(-12.000000, -12.000000) "></path>
                                    </g>
                                </g>
                            </g>
                        </g>
                    </svg>
                </a>"""


def delete_btn(id):
    return f"""<a href="#" onclick="deleteTimeline({id})" tabindex="-1">
                    <svg width="24px" height="24px" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                        <title>Delete</title>
                        <g id="Final---User-Profile" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                            <g id="UserProfile---list" transform="translate(-1381.000000, -308.000000)">
                                <rect fill="#5D3E91" opacity="0" x="0" y="0" width="1440" height="900"></rect>
                                <g id="Group-3-Copy" transform="translate(120.000000, 300.000000)">
                                    <rect id="Rectangle" fill="#F6F4F9" opacity="0" x="0" y="0" width="1300" height="40"></rect>
                                    <g id="Group-2" transform="translate(1227.000000, 8.000000)" fill="#020C2D" fill-opacity="0.5">
                                        <g id="delete" transform="translate(34.000000, 0.000000)">
                                            <path d="M15,7 L9,7 C7.34314575,7 6,8.34314575 6,10 L6,18 C6,19.6568542 7.34314575,21 9,21 L15,21 C16.6568542,21 18,19.6568542 18,18 L18,10 C18,8.34314575 16.6568542,7 15,7 Z M9,9 L15,9 C15.5522847,9 16,9.44771525 16,10 L16,18 C16,18.5522847 15.5522847,19 15,19 L9,19 C8.44771525,19 8,18.5522847 8,18 L8,10 C8,9.44771525 8.44771525,9 9,9 Z M10.5,3 L13.5,3 C14.3284271,3 15,3.67157288 15,4.5 C15,5.32842712 14.3284271,6 13.5,6 L10.5,6 C9.67157288,6 9,5.32842712 9,4.5 C9,3.67157288 9.67157288,3 10.5,3 Z" id="Combined-Shape"></path>
                                        </g>
                                    </g>
                                </g>
                            </g>
                        </g>
                    </svg>
                </a>"""


def duplicate_btn(id):
    return f"""<a href="#" onclick="duplicateTimelineModal({id})" tabindex="-1">
                    <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="20px" height="20px">
                        <path d="M0 0h48v48H0z" fill="none"></path>
                        <path d="M32 2H8C5.79 2 4 3.79 4 6v28h4V6h24V2zm6 8H16c-2.21 0-4 1.79-4 4v28c0 2.21 1.79 4 4 4h22c2.21 0 4-1.79 4-4V14c0-2.21-1.79-4-4-4zm0 32H16V14h22v28z" fill="#7c7f93" class="fill-000000"></path>
                    </svg>
                </a>"""
