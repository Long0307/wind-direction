package com.example.demo.model;

import lombok.Builder;
import lombok.Data;

@Builder @Data
public class SensorGridModel {
	private int grid_num;
	private String gen_time;
	private float upper_left_lot;
	private float upper_left_lat;
	private float upper_right_lot;
	private float upper_right_lat;
	private float lower_right_lot;
	private float lower_right_lat;
	private float lower_left_lot;
	private float lower_left_lat;
	private float center_lot;
	private float center_lat;
	private int section;
}
