#
./bin/logstash --debug -v -e ' input { gelf {  port => 12201 type => 'gelf' } } filter { } output { elasticsearch { index => "gelf-%{+YYYY.MM.dd}" } }'
echo '{"version": "1.1","host":"clickky.biz","short_message":"A short message that helps you identify what is going on","full_message":"Backtrace here\n\nmore stuff","level":1,"_user_id":9001,"_some_info":"foo","_some_env_var":"bar"}' | gzip |nc -w 1 -u localhost 12201
