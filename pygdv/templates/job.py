<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/"
      xmlns:xi="http://www.w3.org/2001/XInclude">

  <xi:include href="master.html" />
  <xi:include href="definitions.html"/>

<head>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
  <title py:replace="page"></title>
</head>
<style>
#menu_items {
  padding:0px 12px 0px 2px;
  list-style-type:None
}
</style>

<body class="tundra">
  
${item_info(info)}

<img src="${tmpl_context.src}"/>


</body>
</html>
