<?xml version="1.0" encoding="iso-8859-15"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" encoding="iso-8859-15"/>
  <xsl:param name="pythondir"/>
  <xsl:template match="import"><import>import fft_web</import></xsl:template>
  <xsl:template match="doc">
  <doc><xsl:value-of select="$pythondir"/>/fft_web.py</doc></xsl:template>
  <!--<xsl:template match="grc_source"><grc_source>/home/mimbert/devel/cortexlab/fft-web.git/grc/fft-web.grc</grc_source></xsl:template>-->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
