package com.example.demo.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.demo.model.EstimateGridSensorDataModel;
import com.example.demo.model.SensorGridModel;
import com.example.demo.service.CmapService;

@RestController
@RequestMapping("/api")
public class ApiController {
	
	@Autowired
	private CmapService cmapService;
	
	@GetMapping("/sensorgrid")
	public List<SensorGridModel> getSensorGrid() {
		return cmapService.getSensorGrid();
	}
	
	@GetMapping("/estimategridsensordata")
	public List<EstimateGridSensorDataModel> getEstimateGridSensorData() {
		return cmapService.getEstimateGridSensorData();
	}
}
