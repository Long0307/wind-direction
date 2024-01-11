package com.example.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.servlet.ModelAndView;

@Controller
public class HomeController {

    @GetMapping("/home")
    public ModelAndView goHome() {
        ModelAndView mav = new ModelAndView();
        mav.setViewName("content/home.html");
        return mav;
    }
}