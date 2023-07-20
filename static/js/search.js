;(function ($) {
    $.fn.customSearch = function (options) {
        var defaults = $.extend({
            loading: function () {
                return new Promise((resolve, reject) => {
                    resolve("default resolve");
                });
            },
            selectElem: $(this),
            closeOnCheck: false,
            maxListValElem: null,
            deSelectTemplate: "",
            scrollCheckElement: "body",
            openMenu: function (elem, isPlugin) {
                $(this).trigger('cs-dropdown-show');
                let target = elem.find('#drop-btn');
                if (isPlugin) {
                    if (!$(elem).hasClass("opened")) {
                        $(elem).addClass("opened");
                        $(elem).find('.multi-select-list-wrap').css("display", "flex");
                        $(this).trigger('cs-dropdown-shown');
                    }
                } else {
                    let par = $(elem).parent();
                    if (!(par.hasClass('opened'))) {
                        par.addClass("opened");
                        par.find(".multi-select-list-wrap").css("display", "flex");
                        $(this).trigger('cs-dropdown-shown');
                    }
                }
            },
            closeMenu: function (elem, isPlugin) {
                if (isPlugin) {
                    let a = elem.find('select').attr('id');
                    $('#' + a).trigger('cs-dropdown-close');
                    $(elem).removeClass("opened");
                    $(elem).find('.multi-select-list-wrap').hide();
                    $('#' + a).trigger('cs-dropdown-closed');
                } else {
                    //$(elem).hide();
                    let par = $(elem).parent();
                    let a = $(elem).attr('id');
                    if ((par.hasClass('opened'))) {
                        $('#' + a).trigger('cs-dropdown-close');
                        par.removeClass("opened");
                        par.find(".multi-select-list-wrap").hide();
                        $('#' + a).trigger('cs-dropdown-closed');
                    }
                }
            },
            destroyFun: function (elem) {
                let dTarget = elem.attr('id');
                let imParent = $('#' + dTarget).parents().eq(1);
                let detachSelect = $('#' + dTarget).clone();
                imParent.append(detachSelect)
                imParent.find('.multi-select').remove();
                $('#' + dTarget).show();
            },
            clearValue: function (elem) {
                console.log(elem.parent().find("#show-value").length);
            },
            updateMenu: function (elem) {
                var parent = $(elem).parent().closest('.multi-select');
                create(parent);
            },
            clickBtnTemplate: "",
            loadingTemplate: `<div class="loading">Loading...</div>`,
            submitBtnText: "Submit",
            targetId: ".selected-ids",
            opentType: 'click',
            hideClearIcon: false,
            popupStyles: '',
            searchStyle: '',
            optionLabelStyle: '',
            listTemplate: '<div class="flex justify-between items-center dropdown-list hover:bg-mild-gray p-3 pb-2 list-option">\n' +
                '    <div class="flex">\n' +
                '       <div class="relative mr-2.5 align-middle w-4 option-input">\n' +
                '           <input type="checkbox" name="toggle" class="cursor-pointer nt w-4 h-4 rounded checked:bg-dark-blue checked:focus:bg-dark-blue checked:hover:bg-dark-blue focus:bg-dark-blue" />\n' +
                '       </div>\n' +
                '       <label class="text-sm font-normal text-dark-black cursor-pointer block -mt-1 option-name"></label>\n' +
                '    </div>\n' +
                '</div>',
            listStyle: '',
            checkboxStyle: '',
            hideSelected: false,
            badgeStyle: '',
            badgeColors: '',
            onItemCheck: function () {
            },
            onSelectOpen: function () {
            },
            onSelectClose: function () {
            },
            defaultCheck: undefined,
            conCurrentSelect: null,
        }, options)

        function getInitialValues(parent) {
            var elem = $(parent).find('select');
            var initialValArray = [];
            if ($(elem).attr("initialValue") && $(elem).attr("initialValue").length > 0) {
                var val = $(elem).attr("initialValue");
                $(elem).val(val);
                if (val.indexOf('[') != -1) {
                    $(parent).find(defaults.targetId).text("");
                    var tempVal = $(elem).attr("initialValue").split("[");
                    tempVal = tempVal[1].split(",");
                    $.each(tempVal, function (key, item) {
                        if (key + 1 == tempVal.length) {
                            initialValArray.push(item.split(']')[0]);
                        } else {
                            if (item != "") {
                                initialValArray.push(item);
                            }
                        }
                    })
                }
            }
            return initialValArray;
        }

        function create(parent) {
            var isMultiple = $(parent).find('select').attr("multiple");
            if ($(parent).find('select').attr('disabled')) {
                $(parent).find("#drop-btn").css({'opacity': '0.5', 'pointer-events': 'none'})
            }
            var initialValArray = getInitialValues(parent);
            var elem = $(parent).find('select');
            var selectOptions = $(elem).children();
            var dropDownList = [];
            var listElem = $(parent).find('#select-list');
            $(listElem).empty();
            $(parent).find('.loading').remove();
            if (selectOptions.length > 0) {
                //Creating Select List UI
                //Creating Select List UI
                // Create List JSON
                $(selectOptions).each(function () {
                    var obj = {};
                    if ($(this).attr("data-addition")) {
                        var addition = $(this).attr("data-addition");
                        obj.addition = addition;
                    }
                    if ($(this).html()) {
                        obj.disable = $(this).attr('disabled') ? true : false;
                        obj.name = $(this).html();
                        obj.val = $(this).val();
                        dropDownList.push(obj);
                    }
                })
                let initialValue = $(elem).attr("initialValue");
                let tempInitialValArr = [];
                if (dropDownList.length > 0) {
                    // Looping list Items
                    $.each(dropDownList, function (key, item) {
                        let tempInitalVal = null;
                        if (initialValArray.length == 0 && (initialValue == item.val || initialValue == item.name)) {
                            $(parent).find(defaults.targetId).text(item.name);
                            tempInitalVal = item.val;
                        } else {
                            if (initialValArray.indexOf(item.val) != -1 || initialValArray.indexOf(item.name) != -1) {
                                tempInitalVal = item.val;
                                tempInitialValArr.push(item.name)
                            }
                        }
                        if (tempInitalVal) {
                            var select = $(parent).find('select option');
                            $(select).each(function () {
                                if (tempInitalVal == $(this).val()) {
                                    $(this).prop("selected", true);
                                }
                            })
                        }
                        let id = Math.floor((Math.random() * 100000) + 1);

                        var elem = `<div class="flex justify-between dropdown-list hover:bg-mild-gray p-3 pb-2 list-option ${tempInitalVal ? "selected focused" : ""}" id="${id}" data-index="${key}" data-list-id="${item.val}">
                                        <div class="flex">
                                           <div class="relative mr-2.5 align-middle w-4 option-input">
                                               <input type="${isMultiple ? "checkbox" : "radio"}" class="${defaults.checkboxStyle} option-input ${tempInitalVal ? "checked" : ""}" name="${isMultiple ? "checkbox" : "radio"}" value="${item.val}" checked='${tempInitalVal ? true : false}'/>
                                           </div>
                                           <label class="option-name ${defaults.optionLabelStyle}">${item.name}</label>
                                        </div>
                                    </div>`;

                        if (false) {
                            var elem = $.parseHTML(defaults.listTemplate);
                            $(elem).attr("data-index", key)
                            $(elem).attr({"id": id, "data-list-id": item.val});
                            $(elem).find('input').attr({
                                type: isMultiple ? "checkbox" : "radio",
                                name: isMultiple ? "checkbox" : "radio",
                                value: item.val
                            });
                            $(elem).find('.option-name').text(item.name);
                            if (tempInitalVal) {
                                $(elem).addClass("selected focused");
                                $(elem).find('input').addClass("checked");
                                $(elem).find('input').attr("checked", true);
                            }
                            $(listElem).append(elem);

                        } else {
                            $(listElem).append(elem);
                        }

                        // To hide Checkbox
                        if (!isMultiple) {
                            $(parent).find('#' + id + ' .option-input').hide();
                        }

                        if (item.disable) {
                            $(parent).find('#' + id).css({'pointer-events': 'none', 'opacity': '0.4'});
                            $(parent).find('#' + id).find('input').attr('disabled', true).css('pointer-events', 'none');
                        }

                        if (item.addition) {
                            if (defaults.badgeColors != '') {
                                var color = item.addition;
                                var style = typeof defaults.badgeColors == 'string' ? defaults.badgeColors : defaults.badgeColors[color];
                                let elem = `<div><span class="addition-badge ${style}">${color}</span></div>`;
                                $(parent).find('#' + id).append(elem);
                            } else {
                                let additionData = item.addition.split(",");
                                for (let i = 0; i < additionData.length; i++) {
                                    let elem = `<div><span class="addition-badge ${defaults.badgeStyle}">${additionData[i]}</span></div>`;
                                    $(parent).find('#' + id).append(elem);
                                }
                            }
                        }
                    })
                } else {
                    $(listElem).append('<div class="no-data-available">No data available</div>')
                }

                if (tempInitialValArr.length > 0) {
                    $.each(tempInitialValArr, function (key, item) {
                        var content = key < tempInitialValArr.length - 1 ? item + ", " : item;
                        $(parent).find(defaults.targetId).append(content);
                    })
                }
            } else {
                $(listElem).append('<div class="no-data-available">No data available</div>');
            }
        }

        return $(defaults.selectElem).each(function () {
            if (defaults.hasOwnProperty(options) == true) {
                var component = $(this);
                return defaults[options](component, false)
            } else {
                var elem = $(this);
                var childern = $(elem).children();
                let multipleCheck = $(elem).attr('multiple');
                $(elem).wrap("<div class='multi-select'></div>");
                $(elem).css('display', 'none');
                var searchArea = `
                <div class='multi-select-inner'>
                    <div id='drop-btn'>Filter</div>
                    <div class="selected-ids"></div>
                    <div class="multi-select-list-wrap z-20 absolute rounded-md bg-white text-dark-black pb-3 block shadow-md w-64 top-10 left-0 max-h-96 overflow-hidden cursor-default z-10 top-13">
                        <div id="cus-search-wrap">
                            <input id="select-search" type="text" value="" autocomplete="off" name="search" placeholder="Search..."/>
                            <span class="search-icon">
                                <svg width="24px" height="24px" viewBox="0 0 24 24" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                                    <title>Search</title>
                                    <defs>
                                        <filter x="-0.6%" y="-2.9%" width="101.2%" height="105.7%" filterUnits="objectBoundingBox" id="filter-1">
                                            <feOffset dx="0" dy="1" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
                                            <feGaussianBlur stdDeviation="1.5" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
                                            <feColorMatrix values="0 0 0 0 0   0 0 0 0 0   0 0 0 0 0  0 0 0 0.12 0" type="matrix" in="shadowBlurOuter1" result="shadowMatrixOuter1"></feColorMatrix>
                                            <feMerge>
                                                <feMergeNode in="shadowMatrixOuter1"></feMergeNode>
                                                <feMergeNode in="SourceGraphic"></feMergeNode>
                                            </feMerge>
                                        </filter>
                                        <rect id="path-2" x="0" y="0" width="256" height="320" rx="10"></rect>
                                        <filter x="-20.5%" y="-16.4%" width="141.0%" height="132.8%" filterUnits="objectBoundingBox" id="filter-4">
                                            <feOffset dx="0" dy="0" in="SourceAlpha" result="shadowOffsetOuter1"></feOffset>
                                            <feGaussianBlur stdDeviation="17.5" in="shadowOffsetOuter1" result="shadowBlurOuter1"></feGaussianBlur>
                                            <feColorMatrix values="0 0 0 0 0.0509803922   0 0 0 0 0.0470588235   0 0 0 0 0.11372549  0 0 0 0.15 0" type="matrix" in="shadowBlurOuter1"></feColorMatrix>
                                        </filter>
                                    </defs>
                                    <g id="UI" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                                        <g id="Timesheet-1---Group---Dropdown-Copy" transform="translate(-579.000000, -199.000000)">
                                            <rect fill="#5D3E91" opacity="0.06" x="0" y="0" width="1440" height="900"></rect>
                                            <g id="list" filter="url(#filter-1)" transform="translate(100.000000, 216.000000)" fill="#FFFFFF">
                                                <rect id="Rectangle" x="0" y="0" width="1340" height="280"></rect>
                                            </g>
                                            <g id="dropdown" transform="translate(559.000000, 184.000000)">
                                                <mask id="mask-3" fill="white">
                                                    <use xlink:href="#path-2"></use>
                                                </mask>
                                                <g id="Rectangle">
                                                    <use fill="black" fill-opacity="1" filter="url(#filter-4)" xlink:href="#path-2"></use>
                                                    <use fill="#FFFFFF" fill-rule="evenodd" xlink:href="#path-2"></use>
                                                </g>
                                                <rect id="Rectangle" fill="#F3F6FF" mask="url(#mask-3)" x="10" y="10" width="236" height="34" rx="10"></rect>
                                                <g id="search-icon" mask="url(#mask-3)">
                                                    <g transform="translate(20.000000, 15.000000)">
                                                        <rect id="Rectangle" fill="#F3F6FF" opacity="0" x="0" y="0" width="24" height="24"></rect>
                                                        <path d="M6.05025253,6.05025253 C8.78392257,3.31658249 13.2160774,3.31658249 15.9497475,6.05025253 C18.4484927,8.5489978 18.6632287,12.4668446 16.5939552,15.2094979 C16.6570068,15.2527187 16.7176613,15.3034478 16.7747054,15.3604918 L20.074537,18.6603235 C20.5301487,19.1159351 20.5829124,19.8018639 20.1923882,20.1923882 C19.8018639,20.5829124 19.1159351,20.5301487 18.6603235,20.074537 L15.3604918,16.7747054 C15.3034478,16.7176613 15.2527187,16.6570068 15.208384,16.5937738 C12.4668446,18.6632287 8.5489978,18.4484927 6.05025253,15.9497475 C3.31658249,13.2160774 3.31658249,8.78392257 6.05025253,6.05025253 Z M7.46446609,7.46446609 C5.51184464,9.41708755 5.51184464,12.5829124 7.46446609,14.5355339 C9.41708755,16.4881554 12.5829124,16.4881554 14.5355339,14.5355339 C16.4881554,12.5829124 16.4881554,9.41708755 14.5355339,7.46446609 C12.5829124,5.51184464 9.41708755,5.51184464 7.46446609,7.46446609 Z" id="Shape" fill-opacity="0.5" fill="#020C2D"></path>
                                                    </g>
                                                </g>
                                            </g>
                                        </g>
                                    </g>
                                </svg>
                            </span>
                        </div>
                        <div class="selected-toggle">
                            <div class="combine-selector-text"></div>
                            <div class="btn-wrap">
                                <span class="select-all-btn">All</span>
                                <span class="deselect-btn">None</span>
                            </div>
                        </div>
                        <div class="select-list-wrap">
                            <div id="select-list" data-select-id="${$(elem).attr("id")}"></div>
                        </div>
                    </div>
                </div>`;
                $(searchArea).insertAfter(elem);
                //Global variable declartion
                var parent = $(elem).parent().closest('.multi-select');
                var closeEvent = 'click';
                var selectedValues = [];
                var selectedTexts = [];

                if (defaults.clickBtnTemplate != '') {
                    $(parent).find('#drop-btn').replaceWith(defaults.clickBtnTemplate);
                }

                function initActions() {
                    if (defaults.defaultCheck) {
                        $.each(defaults.defaultCheck, function (key, item) {
                            selectedValues.push(item);
                            selectedTexts.push(item);
                            $(parent).find(`input[value=${item}]`).attr("checked", true).addClass("checked");
                            $(parent).find(`input[value=${item}]`).closest('.list-option').addClass("selected");
                        })
                        $(elem).val(selectedValues).change();
                        if (!defaults.hideSelected) {
                            showSelected();
                        }
                        defaults.onItemCheck.call(null, selectedValues, selectedTexts);
                    }
                    //Checkbox Click
                    $(parent).find('.list-option').on('click', function (event) {
                        $(parent).find('.list-option').removeClass('focused');
                        $(this).addClass('focused');
                        var value = $(this).find('input').val();
                        var text = $(this).find('.option-name').text();
                        if (!$(this).find('input').attr('disabled')) {
                            if (!multipleCheck) {
                                selectedValues = [];
                                selectedTexts = [];
                            }
                            if (multipleCheck) {
                                if ($(this).find('input')[0].checked == false) {
                                    $(this).addClass('selected');
                                    $(this).find('input').attr('checked', true);
                                    $(this).find('input').addClass('checked');
                                    selectedValues.push(value);
                                    selectedTexts.push(text);
                                } else {
                                    selectedValues = $.grep(selectedValues, function (n) {
                                        return n != value;
                                    })
                                    selectedTexts = $.grep(selectedTexts, function (n) {
                                        return n != text;
                                    })
                                    $(this).removeClass('selected');
                                    $(this).find('input').removeAttr('checked');
                                    $(this).find('input').removeClass('checked');
                                }
                            } else {
                                var listId = $(this).attr('data-list-id');
                                $(parent).find('.list-option.selected input').removeAttr('checked').removeClass('checked');
                                $(parent).find('.list-option.selected').removeClass('selected');
                                selectedValues = [];
                                selectedTexts = [];
                                $(this).addClass('selected');
                                $(this).find('input').attr('checked', true);
                                $(this).find('input').addClass('checked');
                                selectedTexts.push(text);
                                selectedValues.push(value);
                                if (defaults.conCurrentSelect) {
                                    $("[data-select-id=" + defaults.conCurrentSelect + "]").find('.list-option').each(function () {
                                        if ($(this).attr('data-list-id') == listId) {
                                            $(this).find('input').click();
                                        }
                                    })
                                }
                            }

                            if (!multipleCheck) {
                                //Changing select tag value for AJAX call
                                $(elem).val(selectedValues).change();
                                defaults.onItemCheck.call(null, selectedValues, selectedTexts);
                                defaults.closeMenu(parent, true);
                                defaults.onSelectClose.call(null);
                                if (!defaults.hideSelected) {
                                    showSelected();
                                }
                            }
                        }
                    })


                    //submitBtn Click
                    $(parent).find('#submit').on('click', function () {
                        $(elem).val(selectedValues).change();
                        if (!defaults.hideSelected)
                            showSelected();

                        defaults.onItemCheck.call(null, selectedValues, selectedTexts);
                        defaults.closeMenu(parent, true);
                        defaults.onSelectClose.call(null);
                        defaults.selectElem.trigger('cs-submit');
                    })

                    //cancelBtn click
                    $(parent).find("#custom-search-close").on('click', function () {
                        defaults.closeMenu(parent, true);
                        defaults.onSelectClose.call(null);
                    })
                }

                if ($(elem).attr("subtitle")) {
                    $(parent).find(".combine-selector-text").text($(elem).attr("subtitle"));
                } else {
                    $(parent).find(".combine-selector-text").text('Choose Option');
                }

                if (!multipleCheck || childern.length < 1) {
                    $(parent).find(".selected-toggle").remove();
                }

                const searchElem = $(parent).find("#select-search"),
                    selectAll = $(parent).find('.select-all-btn'),
                    dropELem = $(parent).find('#drop-btn'),
                    popUp = $(parent).find('.multi-select-list-wrap'),
                    deCheckElem = $(parent).find('.deselect-btn');

                if (false) {
                    popUp.addClass('z-20 absolute rounded-md bg-white text-dark-black pb-3 block shadow-md w-64 top-10 left-0 max-h-96 overflow-hidden');
                }

                if (defaults.searchStyle != '') {
                    searchElem.addClass(defaults.searchStyle);
                }

                $(parent).find('#select-list').prepend(defaults.loadingTemplate);

                if (!multipleCheck) {
                    $(parent).find('.selected-toggle').remove();
                }

                if (multipleCheck && childern.length > 0) {
                    var submitBtn = `<div style="margin-top: 15px; text-align: right; display: flex;" class="multi-select-submit-wrap">
                                        <div class="text-white cursor-pointer justify-center flex-1 text-center bg-dark-black-50 rounded inline-flex items-center pr-3 pl-2 py-1 ml-2 mr-1 text-sm font-normal" id="custom-search-close">Cancel</div>
                                        <div id='submit' class="text-white cursor-pointer justify-center flex-1 bg-dark-blue rounded inline-flex items-center pr-3 pl-2 py-1 text-sm ml-1 mr-2 font-normal">${defaults.submitBtnText}</div>
                                     </div>`
                    $(parent).find('.multi-select-list-wrap').append(submitBtn);
                }

                //Intializing Element
                defaults.loading.call().then(
                    function (value) {
                        create(parent);
                        initActions();
                    },
                    function (error) {
                        console.log(error);
                    }
                )

                function stringToFloat(str) {
                    if (str) {
                        var tempVal = str.split(":");
                        if (tempVal.length > 0) {
                            var tempString = tempVal[0] + "." + tempVal[1];
                            return parseFloat(tempString);
                        }
                    }
                }


                function removeMinimum(max) {
                    $(parent).find('.list-option').each(function () {
                        var listValue = stringToFloat($(this).find('.option-name').text());
                        if (listValue > max) {
                            $(this).remove();
                        }
                    })
                }

                function popUpPosition(popParent) {
                    var parentTop = $(popParent).offset().top;
                    var parentHeight = $(popParent).find("#drop-btn").innerHeight();
                    var parentLeft = $(popParent).offset().left;
                    var listHeight = $(popParent).find('.multi-select-list-wrap').height();
                    var elemOff = parentTop + listHeight;
                    var elemOff = parentTop + listHeight + parentHeight;

                    if (elemOff + 30 > $('body').height() && elemOff >= 256) {
                        $(popParent).find("#select-list").css({"min-height": "220px", "max-height": "220px"});
                    }

                    listHeight = $(popParent).find('.multi-select-list-wrap').height();
                    elemOff = parentTop + listHeight + parentHeight;

                    if (elemOff > $('body').height()) {
                        $(popParent).find('.multi-select-list-wrap').css({
                            "position": "fixed",
                            "top": parentTop - listHeight - parentHeight + 10,
                            "left": parentLeft
                        })
                    } else {
                        $(popParent).find('.multi-select-list-wrap').css({
                            "position": "fixed",
                            "left": parentLeft,
                            "top": parentTop + parentHeight + 10,
                            "bottom": "auto"
                        })
                    }
                }

                $(defaults.scrollCheckElement).on('scroll', function () {
                    if ($('.multi-select.opened').length > 0) {
                        popUpPosition($('.multi-select.opened'));
                    }
                })
                //open lists
                $(dropELem).on(defaults.opentType, function () {
                    if (!$(parent).find('select').attr('disabled')) {
                        $(parent).find('#select-list')[0].scrollBy({
                            'top': 0,
                            'left': 0,
                            'behavior': 'smooth'
                        });
                        // checking actual selected value
                        var existingValues = $(elem).val();
                        if (defaults.maxListValElem) {
                            if (parseInt($(defaults.maxListValElem).val()) >= 0) {
                                var maxListValue = stringToFloat($(defaults.maxListValElem).val());
                                removeMinimum(maxListValue);
                            } else {
                                return false;
                            }
                        }
                        if (typeof existingValues == 'string') {
                            existingValues = [];
                            existingValues.push($(elem).val())
                        }
                        var index = 0;
                        $(parent).find('.list-option').each(function () {
                            $(this).attr('data-index', index);
                            index = index + 1;
                            var listId = $(this).attr('data-list-id');
                            var listText = $(this).find('.option-name').text();
                            $(this).removeClass('focused');
                            if (existingValues && existingValues.length > 0 && $.inArray(listId, existingValues) != -1) {
                                if ($.inArray(listId, selectedValues) == -1) {
                                    selectedValues.push(listId);
                                    selectedTexts.push(listText);
                                }
                                $(this).addClass('selected');
                                $(this).find('input').attr('checked', true);
                                $(this).find('input').addClass('checked');
                            } else {
                                selectedValues = $.grep(selectedValues, function (n) {
                                    return n != listId;
                                })
                                selectedTexts = $.grep(selectedTexts, function (n) {
                                    return n != listText;
                                })
                                $(this).removeClass('selected');
                                $(this).find('input').removeAttr('checked');
                                $(this).find('input').removeClass('checked');
                            }
                        })
                        popUpPosition(parent);
                        defaults.onSelectOpen.call(null);
                        defaults.openMenu(parent, true);
                        if (searchElem.length > 0) {
                            $(searchElem).val("");
                            $(searchElem).focus();
                            $(parent).find('[data-hide=true]').each(function () {
                                $(this).removeAttr('data-hide');
                                $(this).removeAttr('style');
                            })
                        }
                    }
                })

                // Close list
                if (closeEvent == 'click') {
                    $(document).on(closeEvent, function (event) {
                        if (!($(event.target).closest(parent).length) && $(parent).hasClass("opened") && !($(event.target).hasClass('close-icon'))) {
                            defaults.closeMenu(parent, true);
                            defaults.onSelectClose.call(null);
                        }
                    });
                } else {
                    $(parent).on(closeEvent, function () {
                        if ($(this).hasClass("opened") && !multipleCheck) {
                            defaults.closeMenu(parent, true);
                            defaults.onSelectClose.call(null);
                        }
                    })
                }

                //Keydown events
                $(document).on('keydown', function (event) {
                    if (event.key == "Enter" && $(parent).hasClass("opened")) {
                        //TODO:  var input = $(parent).find('.list-option.focused input');
                        var input = $(parent).find('.list-option.focused');
                        if (input.length > 0) {
                            $(input).click();
                        }
                    }
                    if (event.key == "Escape" && $(parent).hasClass("opened")) {
                        $(parent).find('.list-option').removeClass('focused');
                        $(parent).find('#select-search').blur();
                        defaults.closeMenu(parent, true);
                        defaults.onSelectClose.call(null);
                    }
                    if (event.key == "ArrowDown" && $(parent).hasClass("opened")) {
                        if ($(parent).find('.list-option').hasClass('focused')) {
                            var ele = $(parent).find('.list-option.focused');
                            var next = parseInt(ele.attr("data-index")) + 1;
                            var nextsib = $(parent).find('.list-option[data-index="' + next + '"]');
                            if (nextsib.length > 0) {
                                $(ele).removeClass('focused');
                                $(nextsib).addClass('focused');
                            }
                        } else {
                            var lists = $(parent).find('.list-option[data-index]')[0];
                            $(lists).addClass('focused');
                        }
                        checkScroll("down");
                    }
                    if (event.key == "ArrowUp" && $(parent).hasClass("opened")) {
                        if ($(parent).find('.list-option').hasClass('focused')) {
                            var ele = $(parent).find('.list-option.focused');
                            var prevIndex = parseInt(ele.attr("data-index")) - 1;
                            if ($(ele).prev('.list-option').length > 0) {
                                $(ele).removeClass('focused');
                                $(parent).find('.list-option[data-index="' + prevIndex + '"]').addClass('focused');
                            }
                        }
                        checkScroll("up");
                    }
                });

                function checkScroll(type) {
                    if ($(parent).find('.list-option').hasClass('focused')) {
                        var dropParent = $(parent).find("#select-list");
                        var ele = $(parent).find('.list-option.focused');
                        if ($(ele).length > 0) {
                            var index = parseInt($(ele).attr("data-index"));
                            var listPositiontop = $(ele).offset().top;
                            var scrollElemTop = $(parent).find('#select-list').offset().top;
                            var scrollElem = $(parent).find('#select-list')[0];
                            var scrollElemHeight = $(parent).find('#select-list').innerHeight();
                            var listHeight = $(ele).innerHeight();
                            var el = (listPositiontop + listHeight) - (scrollElemHeight + scrollElemTop);
                            if (type === "down") {
                                if ($(dropParent).find(`[data-index=${index + 1}]`).length > 0) {
                                    var nextsiblinTop = $(dropParent).find(`[data-index=${index + 1}]`).offset().top;
                                    var nextsiblinHe = $(dropParent).find(`[data-index=${index + 1}]`).innerHeight();
                                    el = (nextsiblinHe + nextsiblinTop) - (scrollElemHeight + scrollElemTop) + listHeight;
                                }
                                if (listPositiontop + listHeight > scrollElemHeight + scrollElemTop) {
                                    scrollElem.scrollBy({
                                        'top': el,
                                        'left': 0,
                                        'behavior': 'smooth'
                                    });
                                }
                            } else {
                                if ($(dropParent).find(`[data-index=${index - 1}]`) > 0) {
                                    var nextsiblinTop = $(dropParent).find(`[data-index=${index - 1}]`).offset().top;
                                    var nextsiblinHe = $(dropParent).find(`[data-index=${index - 1}]`).innerHeight();
                                    el = scrollElemTop - nextsiblinTop;
                                } else {
                                    el = listHeight;
                                }
                                if (listPositiontop < scrollElemTop) {
                                    scrollElem.scrollBy({
                                        'top': -el,
                                        'left': 0,
                                        'behavior': 'smooth'
                                    });
                                }
                            }
                        }
                    }
                }

                //Search Function
                $(searchElem).on('keyup', function (e) {
                    if (e.originalEvent.code != "ArrowUp" && e.originalEvent.code != "ArrowDown") {
                        var keyWord = $(this).val().toLowerCase();
                        var selectHtml = $(parent).find('.dropdown-list');
                        var index = 0;
                        if (keyWord != "") {
                            $(selectHtml).each(function () {
                                $(this).removeClass("focused");
                                if (!$(this).text().toLowerCase().includes(keyWord)) {
                                    $(this).attr('data-hide', true);
                                    $(this).removeAttr('data-index');
                                    $(this).hide();
                                } else {
                                    $(this).attr('data-index', index);
                                    index = index + 1;
                                    $(this).removeAttr('data-hide');
                                    $(this).show();
                                }
                            })
                        } else {
                            $(selectHtml).each(function () {
                                $(this).addClass('list-option');
                                $(this).attr('data-index', index);
                                index = index + 1;
                                $(this).show();
                            })
                        }
                    }
                })

                //Selected elements
                function showSelected() {
                    $(parent).find(defaults.targetId).empty();
                    if (multipleCheck && selectedTexts.length > 0) {
                        $.each(selectedTexts, function (key, item) {
                            if (false) {
                                var badge = `<div class="selected-badge"><span>${item}</span><a class='close-icon' data-href="${item}">X</a></div>`;
                                $(parent).find(defaults.targetId).append(badge);
                            } else {
                                var content = key < selectedTexts.length - 1 ? item + ", " : item;
                                $(parent).find(defaults.targetId).append(content);
                            }
                        })
                    } else {
                        if (selectedValues.length == 1) {
                            $(parent).find(defaults.targetId).text(selectedTexts['0']);
                        } else {
                            $(parent).find(defaults.targetId).text("");
                        }
                    }
                    $(parent).find('.close-icon').on('click', function () {
                        var val = $(this).attr('data-href');
                        if (val) {
                            selectedValues = $.grep(selectedValues, function (n) {
                                return n != val;
                            })
                            selectedTexts = $.grep(selectedTexts, function (n) {
                                return n != val;
                            })
                            $(parent).find('input[value=' + val + ']').prop("checked", false);
                            $(this).parent().remove();
                        }
                    })
                    if (!multipleCheck) {
                        defaults.closeMenu(parent, true);
                        defaults.onSelectClose.call(null);
                    }
                }

                // Check All
                $(selectAll).on('click', function () {
                    $(parent).find('.list-option input').each(function () {
                        if (!$(this).closest('.list-option').attr('data-hide') && !$(this).attr('checked')) {
                            var value = $(this).val();
                            var text = $(this).closest('.list-option').find('.option-name').text();
                            $(this).closest('.list-option').removeClass('selected');
                            $(this).closest('.list-option').addClass('selected');
                            $(this).attr('checked', true);
                            selectedValues.push(value);
                            selectedTexts.push(text);
                        }
                    })

                    //Changing select tag value for AJAX call
                    if (!multipleCheck) {
                        $(parent).find('select').val(selectedValues);
                        defaults.onItemCheck.call(null, selectedValues, selectedTexts);
                    }


                    if (!defaults.hideSelected && !multipleCheck)
                        showSelected();
                })

                // Decheck All
                $(deCheckElem).on('click', function () {
                    if (!multipleCheck) {
                        var elem = $(parent).find('.list-option.selected');
                        if (elem.length > 0) {
                            $(elem).find('input').removeClass('checked').removeAttr('checked');
                            $(elem).removeClass('selected');
                            selectedValues = [];
                            selectedTexts = [];
                        }
                    } else {
                        $(parent).find('.list-option input').each(function () {
                            if (!$(this).closest('.list-option').attr('data-hide')) {
                                var val = $(this).val();
                                var text = $(this).closest('.list-option').find('.option-name').text();
                                selectedValues = $.grep(selectedValues, function (n) {
                                    return n != val;
                                })
                                selectedTexts = $.grep(selectedTexts, function (n) {
                                    return n != text;
                                })
                                $(this).removeAttr('checked');
                                $(this).removeClass("checked");
                                $(this).closest('.list-option').removeClass('selected');
                                $(selectAll).prop("checked", false);
                            }
                        })
                    }
                    if (!multipleCheck) {
                        //Changing select tag value for AJAX call
                        $(parent).find('select').val(selectedValues)
                        defaults.onItemCheck.call(null, selectedValues, selectedTexts);
                    }

                    if (!defaults.hideSelected && !multipleCheck)
                        showSelected();
                })
            }
        })
    }
})(jQuery)
