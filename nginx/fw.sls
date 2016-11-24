{% if grains['os'] == 'Debian' %}
netfilter-persistent:
  pkg:
    - installed
iptables-persistent:
  pkg:
    - installed
{% endif %}

createRulesDir:
  cmd.run:
    - name: mkdir /etc/iptables/
    - unless: ls /etc/iptables/

/etc/iptables/rules.v4:
  file.managed:
    - source: http://salt.example.com/fw?env=prod&ipv=4&fwrules=1&server={{ grains.s_hostname }}
    - source_hash: http://salt.example.com/fw?env=prod&ipv=4&hash=1&server={{ grains.s_hostname }}
    - user: root
    - group: root
    - mode: 644
    - backup: minion
  cmd.run:
    - name: service netfilter-persistent reload
    - onchanges:
      - file: /etc/iptables/rules.v4


/etc/iptables/rules.v6:
  file.managed:
    - source: http://salt.example.com/fw?env=prod&ipv=6&fwrules=1&server={{ grains.s_hostname }}
    - source_hash: http://salt.example.com/fw?env=prod&ipv=6&hash=1&server={{ grains.s_hostname }}
    - user: root
    - group: root
    - mode: 644
    - backup: minion
  cmd.run:
    - name: service netfilter-persistent reload
    - onchanges:
      - file: /etc/iptables/rules.v6
