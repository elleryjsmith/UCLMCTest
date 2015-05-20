if javac -cp .:parsing:stanford-corenlp-3.5.0.jar:java-json.jar ./parsing/Parse.java; then
java -cp .:parsing:stanford-corenlp-3.5.0-models.jar:stanford-corenlp-3.5.0.jar:java-json.jar -Xmx3G ./parsing/Parse "$@"
fi