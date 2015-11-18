# Created by palickaa at 14/11/15
Feature: Data Import
  Imports data and converts them into feature vectors

  Scenario: Load data from a folder
    When we want to extract feature vector from first 60 seconds from data in "data/test_files"
    Then we expect to get vectors of length 44100 * 60 + 1
    And we expect to get mapping of genres to discrete numbers