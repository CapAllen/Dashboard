"use strict";

$(function() {

  var sidebarColors = "sidebar-default sidebar-yellow sidebar-bleachedcedar sidebar-light-blue sidebar-gray sidebar-bluegray sidebar-cyan sidebar-red sidebar-orange sidebar-lime sidebar-deep-orange sidebar-light-green sidebar-green sidebar-pink sidebar-deep-purple sidebar-amber sidebar-brown sidebar-midnightblue sidebar-blue sidebar-teal sidebar-purple sidebar-indigo navbar-default navbar-bluegray navbar-amber navbar-deep-purple navbar-light-blue navbar-brown navbar-orange navbar-pink navbar-bleachedcedar navbar-lime navbar-red navbar-deep-orange navbar-yellow navbar-blue navbar-teal navbar-light-green navbar-purple navbar-gray navbar-green navbar-indigo navbar-cyan";
  var headerColors = "navbar-default navbar-gray navbar-bleachedcedar navbar-bluegray navbar-green navbar-orange navbar-pink navbar-blue navbar-deep-orange navbar-lime navbar-yellow navbar-light-blue navbar-light-green navbar-deep-purple navbar-brown navbar-amber navbar-teal navbar-red navbar-purple navbar-indigo navbar-cyan";
  var brandColors = "brand-default brand-gray brand-bleachedcedar brand-bluegray brand-green brand-orange brand-pink brand-blue brand-deep-orange brand-lime brand-yellow brand-light-blue brand-light-green brand-deep-purple brand-brown brand-amber brand-teal brand-red brand-purple brand-indigo brand-cyan";
  
  
  $("#reset-local").on("click", function () {
    $('body .navbar-header').attr("class", "navbar-header");
    $('body nav.navbar').attr("class", "navbar");
    $('aside.sidebar').removeClass(sidebarColors);
    $("body").removeClass("fixed-all boxed-layout fixed-sidebar light-menu icon-menu horizontal-menu");
    $("#fixed-menu, #boxed-layout, #fixed-sidebar, #light-menu, #icon-menu, #horizontal-menu").prop("checked", false);
    localStorage.clear();
  });

  var navColor = localStorage.getItem('navbar-color');
  if (navColor) {
    $('body nav.navbar').removeClass(headerColors).addClass(navColor);
  }

  var sideColor = localStorage.getItem('sidebar-color');
  if (sideColor) {
    $('aside.sidebar').removeClass(sidebarColors).addClass(sideColor);
//    $('#headernav').removeClass(sidebarColors).addClass('navbar-' + sideColor.replace('sidebar-', ''));
  }

  var brandColor = localStorage.getItem('brand-color');
  if (brandColor) {
    $('body .navbar-header').removeClass(brandColors).addClass(brandColor);
  }

  //Show Switcher
  $(".demo-switcher").on("click", function () {
    $('.demo-options').toggleClass("active");
    $(this).toggleClass("btn-danger");
  });


  $('.leftbar-switcher').on("click", function () {
    var className = $(this).attr('data-addclass');
    $('aside.sidebar').removeClass(sidebarColors).addClass(className);
    var horizontalClass = 'navbar-' + className.replace('sidebar-', '');
//    $('#headernav').removeClass(sidebarColors).addClass(horizontalClass);
    localStorage.setItem('sidebar-color', className);
    if(className != "sidebar-default"){
    $("#light-menu").prop("checked", true);
    $("body").addClass("light-menu");
      if (localStorageSupport) {
        localStorage.setItem("lightMenu", 'on');
      }
    }
    else{
      $("#light-menu").prop("checked", false);
      $("body").removeClass("light-menu");
      if (localStorageSupport) {
        localStorage.setItem("lightMenu", 'off');
      }
    }
  });

  $('.topnav-switcher').on("click", function () {
    var className = $(this).attr('data-addclass');
    $('body nav.navbar').removeClass(headerColors).addClass(className);
    localStorage.setItem('navbar-color', className);
  });

  $('.brand-switcher').on("click", function () {
    var className = $(this).attr('data-addclass');
    $('body .navbar-header').removeClass(brandColors).addClass(className);
    localStorage.setItem('brand-color', className);
  });
});

//Fixed Menu
  if (localStorageSupport) {

    var fixedMenu = localStorage.getItem("fixedMenu");

    if (fixedMenu == 'on') {
      $("body").addClass("fixed-all");
      $(".side-panel .tab-pane").css("height", $(window).height() - 130 + "px");
      $("#fixed-menu").prop("checked", true);
    }

    if (fixedMenu == 'off') {
      $("body").removeClass("fixed-all");
      $(".side-panel .tab-pane").css("height", "auto");
    }
  }

  $("#fixed-menu").on("change", function () {
    if ($(this).is(":checked")) {
      $("body").addClass("fixed-all");
      $(".side-panel .tab-pane").css("height", $(window).height() - 130 + "px");
      if (localStorageSupport) {
        localStorage.setItem("fixedMenu", 'on');
      }
    } else {
      $("body").removeClass("fixed-all");
      $(".side-panel .tab-pane").css("height", "auto");
      if (localStorageSupport) {
        localStorage.setItem("fixedMenu", 'off');
      }
    }
  });

  //Boxed layout
  if (localStorageSupport) {

    var boxedLayout = localStorage.getItem("boxedLayout");

    if (boxedLayout == 'on') {
      $("body").addClass("boxed-layout");
      $("#boxed-layout").prop("checked", true);
    }

    if (boxedLayout == 'off') {
      $("body").removeClass("boxed-layout");
    }
  }

  $("#boxed-layout").on("change", function () {
    if ($(this).is(":checked")) {
      $("body").addClass("boxed-layout");
      if (localStorageSupport) {
        localStorage.setItem("boxedLayout", 'on');
      }
    } else {
      $("body").removeClass("boxed-layout");
      if (localStorageSupport) {
        localStorage.setItem("boxedLayout", 'off');
      }
    }
  });

  //Fixed Sidebar
  if (localStorageSupport) {

    var fixedSidebar = localStorage.getItem("fixedSidebar");

    if (fixedSidebar == 'on') {
      $("body").addClass("fixed-sidebar");
      $("#fixed-sidebar").prop("checked", true);
    }

    if (fixedSidebar == 'off') {
      $("body").removeClass("fixed-sidebar");
    }
  }

  $("#fixed-sidebar").on("change", function () {
    if ($(this).is(":checked")) {
      $("body").addClass("fixed-sidebar");
      if (localStorageSupport) {
        localStorage.setItem("fixedSidebar", 'on');
      }
    } else {
      $("body").removeClass("fixed-sidebar");
      if (localStorageSupport) {
        localStorage.setItem("fixedSidebar", 'off');
      }
    }
  });

  //Light menu
  if (localStorageSupport) {

    var lightMenu = localStorage.getItem("lightMenu");

    if (lightMenu == 'on') {
      $("body").addClass("light-menu");
      $("#light-menu").prop("checked", true);
    }

    if (lightMenu == 'off') {
      $("body").removeClass("light-menu");
    }
  }

  $("#light-menu").on("change", function () {
    if ($(this).is(":checked")) {
      $("body").addClass("light-menu");
      if (localStorageSupport) {
        localStorage.setItem("lightMenu", 'on');
      }
    } else {
      $("body").removeClass("light-menu");
      if (localStorageSupport) {
        localStorage.setItem("lightMenu", 'off');
      }
    }
  });

//Icon Menu
  if (localStorageSupport) {

    var iconMenu = localStorage.getItem("iconMenu");

    if (iconMenu == 'on') {
      $("body").addClass("icon-menu");
      $("#icon-menu").prop("checked", true);
      $("#horizontal-menu").removeAttr("disabled");
    }

    if (iconMenu == 'off') {
      $("body").removeClass("icon-menu horizontal-menu");
      $("#horizontal-menu").attr("disabled", "disabled");
      if ($("#horizontal-menu").is(":checked")){
        $("#horizontal-menu").prop("checked", false);  
      }
    }
  }

  $("#icon-menu").on("change", function () {
    if ($(this).is(":checked")) {
      $("body").addClass("icon-menu");
      $("#horizontal-menu").removeAttr("disabled");
      if (localStorageSupport) {
        localStorage.setItem("iconMenu", 'on');
      }
    } else {
      $("body").removeClass("icon-menu horizontal-menu");
      $("#horizontal-menu").attr("disabled", "disabled");
      if ($("#horizontal-menu").is(":checked")){
        $("#horizontal-menu").prop("checked", false);  
      }
      if (localStorageSupport) {
        localStorage.setItem("iconMenu", 'off');
      }
    }
  });

  //Horizontal Icon Menu
  if (localStorageSupport) {

    var horizontalMenu = localStorage.getItem("horizontalMenu");

    if (horizontalMenu == 'on') {
      $("body").addClass("horizontal-menu");
      $("#horizontal-menu").prop("checked", true);
    }

    if (horizontalMenu == 'off') {
      $("body").removeClass("horizontal-menu");
    }
  }

  $("#horizontal-menu").on("change", function () {
    if ($(this).is(":checked") && $("body").hasClass("icon-menu")) {
      
      $("body").addClass("horizontal-menu");

      if (localStorageSupport) {
        localStorage.setItem("horizontalMenu", 'on');
      }
    } else {
      
      $("body").removeClass("horizontal-menu");

      if (localStorageSupport) {
        localStorage.setItem("horizontalMenu", 'off');
      }
    }
  });

// check if browser support HTML5 local storage
function localStorageSupport() {
  return (('localStorage' in window) && window['localStorage'] !== null);
}



if($(window).width() > 768){
  $(".demo-options").mCustomScrollbar({
    theme: "minimal-dark",
    scrollInertia: 0,
    mouseWheel:{
      preventDefault: true
    }
  });
}
else{
  $(".demo-options").css("overflow-y", "auto");
}

