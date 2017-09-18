# Token-Masher
Tool for associating tokens with the cards that makes them

Inputs:
  * A set in xml format from https://github.com/Cockatrice/Magic-Spoiler/tree/files
  * tokens.xml from https://github.com/Cockatrice/Magic-Token
  
Output:
  * A setCode_tokens.xml file containing the tokens from the same set as the input, with added reverse-related fields

Installation:
  * Save setCode_tokens.xml file to your cockatrice customsets directory

Usage:
  * Requires python 2.7 and the modules `re` and `requests`
  * Overwrite the setCode preset with the name of the matching file in https://github.com/Cockatrice/Magic-Spoiler/tree/files
  * Note: the setCode.xml and raw_tokens are just caches created during running, and are not used as inputs
