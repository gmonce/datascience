<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">
<html>
<head>
<link rel="stylesheet" type="text/css" href="bioscope.css" />
</head>
<body>
<h2>Bioscope corpus, analizado</h2>
<xsl:apply-templates />
</body>
</html>
</xsl:template>

<xsl:template match="DocumentSet/Document">
	
	<table>
	<tr><td colspan="2"> <Documento>Documento:<xsl:value-of select="DocID"/>
	
		<td><a><xsl:attribute name="href">
			<xsl:text>bioscope/a</xsl:text>
			<xsl:value-of select="DocID"/> 
			<xsl:text>.bioscope</xsl:text>
			</xsl:attribute> 
			Bioscope
	       </a></td>



		<td><a><xsl:attribute name="href">
			<xsl:text>event/a</xsl:text>
		        <xsl:value-of select="DocID"/> 
		        <xsl:text>.event.xml</xsl:text>
			</xsl:attribute> 
			Genia Event
	       </a></td>



	
	</Documento></td></tr>



	<xsl:apply-templates />
	</table>
	<hr/>
</xsl:template>

<xsl:template match="DocID"/>


<xsl:template match="sentence">
	<tr><td><SentenceId><xsl:value-of select="@id"/></SentenceId></td>
	<td><SentenceText><xsl:copy-of select="."/></SentenceText> </td>

	<td><a><xsl:attribute name="href">
		<xsl:text>img/a</xsl:text>
	        <xsl:value-of select="../../DocID"/> 
	        <xsl:text>.</xsl:text>
	        <xsl:value-of select="@id"/>
	        <xsl:text>.svg</xsl:text>
		</xsl:attribute> 
		Tree
       </a></td>

	<td><a><xsl:attribute name="href">
		<xsl:text>attributes/a</xsl:text>
	        <xsl:value-of select="../../DocID"/> 
	        <xsl:text>.</xsl:text>
	        <xsl:value-of select="@id"/>
	        <xsl:text>.html</xsl:text>
		</xsl:attribute> 
		Attributes
       </a></td>



	</tr>
</xsl:template>

</xsl:stylesheet>

