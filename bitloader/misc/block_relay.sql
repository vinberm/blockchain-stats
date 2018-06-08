/*
Navicat MySQL Data Transfer

Source Server         : bitcoin
Source Server Version : 50630
Source Host           : 106.185.41.188:3306
Source Database       : bitcoin

Target Server Type    : MYSQL
Target Server Version : 50630
File Encoding         : 65001

Date: 2016-06-10 01:22:01
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for block_relay
-- ----------------------------
DROP TABLE IF EXISTS `block_relay`;
CREATE TABLE `block_relay` (
  `block_id` int(11) NOT NULL,
  `relay` char(32) CHARACTER SET utf8 DEFAULT NULL,
  `size` int(11) DEFAULT NULL,
  `ntime` decimal(16,0) DEFAULT NULL,
  `block_fee` decimal(20,0) DEFAULT NULL,
  PRIMARY KEY (`block_id`),
  KEY `ntime` (`ntime`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
